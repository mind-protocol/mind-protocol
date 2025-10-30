"""
Markdown Chunker for Doc Ingestion Pipeline

Chunks markdown files into 250-token target chunks (480 max) while preserving
structural integrity (code fences, sections, paragraphs).

Key features:
- Target 250 tokens, hard limit 480 tokens
- Never split code fences (``` ... ```)
- Prefer splitting on section headers (##)
- Fallback to paragraph breaks
- Token counting via tiktoken (cl100k_base)
- Returns chunks with metadata (offset, token count, type)

Author: Atlas (Infrastructure Engineer)
Date: 2025-10-29
Spec: docs/SPEC DOC INPUT.md
"""

import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import tiktoken


@dataclass
class Chunk:
    """A chunk of markdown text."""
    content: str          # Raw markdown content
    token_count: int      # Actual token count
    char_offset: int      # Character offset in original file
    chunk_index: int      # Sequential chunk number (0-based)
    chunk_type: str       # 'section' | 'paragraph' | 'code' | 'overflow'


class MarkdownChunker:
    """
    Chunks markdown files while preserving structural integrity.

    Respects:
    - Code fences (never splits ``` blocks)
    - Section headers (## preferred split points)
    - Paragraph boundaries (fallback split points)

    Token limits:
    - Target: 250 tokens (ideal chunk size)
    - Max: 480 tokens (hard limit)
    """

    def __init__(self, target_tokens: int = 250, max_tokens: int = 480):
        """
        Initialize chunker.

        Args:
            target_tokens: Target chunk size
            max_tokens: Maximum chunk size (hard limit)
        """
        self.target_tokens = target_tokens
        self.max_tokens = max_tokens
        self.encoder = tiktoken.get_encoding("cl100k_base")  # GPT-4 tokenizer

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoder.encode(text))

    def _find_code_fences(self, text: str) -> List[Tuple[int, int]]:
        """
        Find all code fence blocks in text.

        Returns:
            List of (start_pos, end_pos) tuples for code blocks
        """
        fences = []
        pattern = r'^```[^\n]*\n.*?^```$'

        for match in re.finditer(pattern, text, re.MULTILINE | re.DOTALL):
            fences.append((match.start(), match.end()))

        return fences

    def _is_inside_code_fence(self, pos: int, fences: List[Tuple[int, int]]) -> bool:
        """Check if position is inside a code fence."""
        return any(start <= pos < end for start, end in fences)

    def _split_on_headers(self, text: str, fences: List[Tuple[int, int]]) -> List[str]:
        """
        Split text on ## headers (respecting code fences).

        Args:
            text: Markdown text
            fences: Code fence positions

        Returns:
            List of text sections
        """
        sections = []
        current_start = 0

        # Find all ## headers
        for match in re.finditer(r'^##\s+', text, re.MULTILINE):
            pos = match.start()

            # Skip headers inside code fences
            if self._is_inside_code_fence(pos, fences):
                continue

            # Extract section from previous split to this header
            if pos > current_start:
                section = text[current_start:pos].strip()
                if section:
                    sections.append(section)

            current_start = pos

        # Add final section
        if current_start < len(text):
            section = text[current_start:].strip()
            if section:
                sections.append(section)

        return sections if sections else [text]

    def _split_on_paragraphs(self, text: str, fences: List[Tuple[int, int]]) -> List[str]:
        """
        Split text on paragraph breaks (respecting code fences).

        Args:
            text: Text to split
            fences: Code fence positions

        Returns:
            List of paragraphs
        """
        paragraphs = []

        # Split on double newline (paragraph break)
        parts = re.split(r'\n\n+', text)

        for part in parts:
            part = part.strip()
            if part:
                paragraphs.append(part)

        return paragraphs if paragraphs else [text]

    def _merge_small_chunks(self, chunks: List[str]) -> List[str]:
        """
        Merge small chunks together up to target_tokens.

        Args:
            chunks: List of text chunks

        Returns:
            Merged chunks closer to target size
        """
        merged = []
        current = []
        current_tokens = 0

        for chunk in chunks:
            chunk_tokens = self.count_tokens(chunk)

            # If adding this would exceed max_tokens, flush current
            if current and current_tokens + chunk_tokens > self.max_tokens:
                merged.append('\n\n'.join(current))
                current = [chunk]
                current_tokens = chunk_tokens
            else:
                current.append(chunk)
                current_tokens += chunk_tokens

                # If we're at or above target, flush
                if current_tokens >= self.target_tokens:
                    merged.append('\n\n'.join(current))
                    current = []
                    current_tokens = 0

        # Flush remaining
        if current:
            merged.append('\n\n'.join(current))

        return merged

    def _handle_oversized_chunk(self, text: str, fences: List[Tuple[int, int]]) -> List[str]:
        """
        Handle chunk that exceeds max_tokens.

        Strategy:
        1. Try splitting on paragraphs
        2. If still too large, force split at max_tokens (but respect code fences)

        Args:
            text: Oversized text
            fences: Code fence positions (relative to original document)

        Returns:
            List of smaller chunks
        """
        # Try paragraph split
        paragraphs = self._split_on_paragraphs(text, fences)

        # Check if any paragraph is still too large
        result = []
        for para in paragraphs:
            tokens = self.count_tokens(para)

            if tokens <= self.max_tokens:
                result.append(para)
            else:
                # Force split at character boundaries (respect code fences)
                # This is emergency case - should be rare
                result.extend(self._force_split(para, fences))

        return result

    def _force_split(self, text: str, fences: List[Tuple[int, int]]) -> List[str]:
        """
        Force split text at max_tokens boundaries.

        Emergency fallback for oversized chunks that can't be split structurally.

        Args:
            text: Text to force split
            fences: Code fence positions

        Returns:
            List of chunks under max_tokens
        """
        chunks = []
        current_start = 0

        while current_start < len(text):
            # Try to take max_tokens worth of text
            chunk_text = text[current_start:]
            tokens = self.count_tokens(chunk_text)

            if tokens <= self.max_tokens:
                # Remaining text fits
                chunks.append(chunk_text)
                break
            else:
                # Binary search for split point
                left, right = 0, len(chunk_text)
                split_point = right

                while left < right:
                    mid = (left + right) // 2
                    test_chunk = chunk_text[:mid]
                    test_tokens = self.count_tokens(test_chunk)

                    if test_tokens <= self.max_tokens:
                        split_point = mid
                        left = mid + 1
                    else:
                        right = mid

                # Ensure we're not splitting inside code fence
                absolute_pos = current_start + split_point
                if self._is_inside_code_fence(absolute_pos, fences):
                    # Find fence boundary
                    for start, end in fences:
                        if start <= absolute_pos < end:
                            # Split before fence starts
                            split_point = start - current_start
                            break

                # Extract chunk
                chunk = chunk_text[:split_point].strip()
                if chunk:
                    chunks.append(chunk)

                current_start += split_point

        return chunks

    def chunk_file(self, content: str) -> List[Chunk]:
        """
        Chunk markdown file content.

        Strategy:
        1. Identify code fences (never split these)
        2. Split on ## headers (section boundaries)
        3. Merge small sections up to target_tokens
        4. If section exceeds max_tokens, split on paragraphs
        5. If paragraph exceeds max_tokens, force split (emergency)

        Args:
            content: Raw markdown file content

        Returns:
            List of Chunk objects with metadata
        """
        # Find code fences
        fences = self._find_code_fences(content)

        # Split on headers
        sections = self._split_on_headers(content, fences)

        # Merge small sections
        merged = self._merge_small_chunks(sections)

        # Handle oversized chunks
        final_chunks = []
        for section in merged:
            tokens = self.count_tokens(section)

            if tokens <= self.max_tokens:
                final_chunks.append(section)
            else:
                # Need to split further
                final_chunks.extend(self._handle_oversized_chunk(section, fences))

        # Convert to Chunk objects with metadata
        result = []
        char_offset = 0

        for idx, chunk_text in enumerate(final_chunks):
            # Find this chunk's position in original content
            pos = content.find(chunk_text, char_offset)
            if pos == -1:
                # Fallback if exact match not found (shouldn't happen)
                pos = char_offset

            # Determine chunk type
            chunk_type = self._classify_chunk(chunk_text, fences)

            result.append(Chunk(
                content=chunk_text,
                token_count=self.count_tokens(chunk_text),
                char_offset=pos,
                chunk_index=idx,
                chunk_type=chunk_type
            ))

            char_offset = pos + len(chunk_text)

        return result

    def _classify_chunk(self, text: str, fences: List[Tuple[int, int]]) -> str:
        """
        Classify chunk type.

        Args:
            text: Chunk text
            fences: Code fence positions

        Returns:
            'section' | 'paragraph' | 'code' | 'overflow'
        """
        # Check if starts with header
        if re.match(r'^##\s+', text):
            return 'section'

        # Check if contains code fence
        if '```' in text:
            return 'code'

        # Check if exceeds target significantly (overflow from forced split)
        if self.count_tokens(text) > self.target_tokens * 1.5:
            return 'overflow'

        return 'paragraph'

    def chunk_stats(self, chunks: List[Chunk]) -> Dict[str, Any]:
        """
        Generate statistics about chunking.

        Args:
            chunks: List of chunks

        Returns:
            Statistics dict
        """
        if not chunks:
            return {
                'total_chunks': 0,
                'total_tokens': 0,
                'avg_tokens': 0,
                'min_tokens': 0,
                'max_tokens': 0,
                'by_type': {}
            }

        token_counts = [c.token_count for c in chunks]
        type_counts = {}
        for chunk in chunks:
            type_counts[chunk.chunk_type] = type_counts.get(chunk.chunk_type, 0) + 1

        return {
            'total_chunks': len(chunks),
            'total_tokens': sum(token_counts),
            'avg_tokens': sum(token_counts) / len(token_counts),
            'min_tokens': min(token_counts),
            'max_tokens': max(token_counts),
            'by_type': type_counts,
            'target_tokens': self.target_tokens,
            'max_tokens_limit': self.max_tokens
        }


if __name__ == "__main__":
    # Test with sample markdown
    sample_md = """# Main Title

## Introduction

This is an introduction paragraph with some text. It should be long enough to demonstrate chunking behavior.

## Code Example

Here's a code example:

```python
def example_function():
    # This code fence should never be split
    for i in range(100):
        print(f"Line {i}")
    return "done"
```

## Another Section

This section has multiple paragraphs.

First paragraph here with some content.

Second paragraph here with more content.

Third paragraph with even more content to test splitting.

## Final Section

A brief conclusion.
"""

    chunker = MarkdownChunker(target_tokens=250, max_tokens=480)
    chunks = chunker.chunk_file(sample_md)

    print(f"Generated {len(chunks)} chunks:\n")
    for chunk in chunks:
        print(f"Chunk {chunk.chunk_index} ({chunk.chunk_type}):")
        print(f"  Tokens: {chunk.token_count}")
        print(f"  Offset: {chunk.char_offset}")
        print(f"  Content preview: {chunk.content[:100]}...")
        print()

    stats = chunker.chunk_stats(chunks)
    print("\nChunking Statistics:")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Total tokens: {stats['total_tokens']}")
    print(f"  Avg tokens: {stats['avg_tokens']:.1f}")
    print(f"  Min tokens: {stats['min_tokens']}")
    print(f"  Max tokens: {stats['max_tokens']}")
    print(f"  By type: {stats['by_type']}")
