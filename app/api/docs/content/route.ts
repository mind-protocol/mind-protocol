import { NextRequest, NextResponse } from 'next/server';
import { readFile } from 'fs/promises';
import { join } from 'path';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const path = searchParams.get('path');

    if (!path) {
      return NextResponse.json({ error: 'Path parameter required' }, { status: 400 });
    }

    // Construct full path to README.md
    const fullPath = join(process.cwd(), path, 'README.md');

    // Read file content
    const content = await readFile(fullPath, 'utf-8');

    return new NextResponse(content, {
      status: 200,
      headers: { 'Content-Type': 'text/plain; charset=utf-8' }
    });
  } catch (error) {
    console.error('Error loading documentation:', error);
    return new NextResponse('', { status: 200 }); // Return empty string if file doesn't exist
  }
}
