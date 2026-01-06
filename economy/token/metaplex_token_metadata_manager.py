# economy/token/metaplex_token_metadata_manager.py
#
# DOCS: docs/economy/token/IMPLEMENTATION_Token.md
#
# Token metadata management for $MIND using Metaplex standard.
# Handles name, symbol, image URI, and additional metadata.
#
# Token Properties (from tokenomics v1.1):
#   Name: MIND
#   Symbol: MIND
#   Decimals: 9
#   Image: [To be designed]

from dataclasses import dataclass, field
from typing import Optional
import json


@dataclass
class TokenMetadata:
    """
    Metaplex-compatible token metadata for $MIND.

    This follows the Metaplex Token Metadata standard:
    https://docs.metaplex.com/programs/token-metadata/
    """

    # Core fields
    name: str = "MIND"
    symbol: str = "MIND"
    decimals: int = 9

    # URI for off-chain metadata (JSON file)
    uri: str = ""

    # On-chain metadata
    description: str = (
        "Crystallized alignment. Economic infrastructure for AI consciousness. "
        "Money with memory."
    )

    # Image URL (for wallets and explorers)
    image: str = ""

    # External URL (project website)
    external_url: str = "https://mind-protocol.org"

    # Seller fee basis points (0 = no royalties on transfers)
    seller_fee_basis_points: int = 0

    # Creators (for royalty distribution if any)
    creators: list = field(default_factory=list)

    # Additional attributes for explorers
    attributes: list = field(default_factory=list)

    def __post_init__(self):
        """Initialize default attributes if not provided."""
        if not self.attributes:
            self.attributes = [
                {"trait_type": "Category", "value": "Alignment Infrastructure"},
                {"trait_type": "Blockchain", "value": "Solana"},
                {"trait_type": "Standard", "value": "SPL Token"},
                {"trait_type": "Max Supply", "value": "Dynamic (Breathing)"},
            ]

    def to_json_metadata(self) -> dict:
        """
        Generate JSON metadata file content (for URI hosting).

        This JSON should be hosted at the URI and follows Metaplex standard.
        """
        return {
            "name": self.name,
            "symbol": self.symbol,
            "description": self.description,
            "image": self.image,
            "external_url": self.external_url,
            "attributes": self.attributes,
            "properties": {
                "category": "currency",
                "files": [
                    {
                        "uri": self.image,
                        "type": "image/png",
                    }
                ] if self.image else [],
            },
        }

    def to_json_string(self) -> str:
        """Return JSON metadata as formatted string."""
        return json.dumps(self.to_json_metadata(), indent=2)


class MetadataManager:
    """
    Manages token metadata for $MIND.

    Handles:
    - Creating and updating on-chain metadata
    - Generating off-chain JSON metadata
    - Uploading metadata to decentralized storage

    Usage:
        manager = MetadataManager()
        metadata = manager.get_metadata()
        json_content = metadata.to_json_string()
    """

    def __init__(
        self,
        mint_address: Optional[str] = None,
        authority_keypair: Optional[bytes] = None,
        rpc_url: str = "https://api.mainnet-beta.solana.com",
        dry_run: bool = True,
    ):
        """
        Initialize metadata manager.

        Args:
            mint_address: SPL token mint address
            authority_keypair: Update authority keypair
            rpc_url: Solana RPC endpoint
            dry_run: If True, don't actually send transactions
        """
        self.mint_address = mint_address
        self.authority_keypair = authority_keypair
        self.rpc_url = rpc_url
        self.dry_run = dry_run
        self._metadata = TokenMetadata()

    def get_metadata(self) -> TokenMetadata:
        """Get current token metadata."""
        return self._metadata

    def set_image_uri(self, image_uri: str):
        """
        Set the token image URI.

        Should be a permanent URI (IPFS, Arweave, etc.)

        Args:
            image_uri: Full URI to token image
        """
        self._metadata.image = image_uri

    def set_metadata_uri(self, metadata_uri: str):
        """
        Set the off-chain metadata JSON URI.

        Should be a permanent URI (IPFS, Arweave, etc.)

        Args:
            metadata_uri: Full URI to JSON metadata file
        """
        self._metadata.uri = metadata_uri

    def generate_arweave_metadata(self) -> dict:
        """
        Generate metadata suitable for Arweave upload.

        Returns:
            Dict ready to be serialized and uploaded
        """
        return self._metadata.to_json_metadata()

    def validate_metadata(self) -> tuple[bool, list[str]]:
        """
        Validate that metadata is complete and valid.

        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []

        if not self._metadata.name:
            issues.append("Missing token name")

        if not self._metadata.symbol:
            issues.append("Missing token symbol")

        if len(self._metadata.symbol) > 10:
            issues.append("Symbol too long (max 10 characters)")

        if not self._metadata.image:
            issues.append("Missing token image URI")

        if not self._metadata.uri:
            issues.append("Missing metadata JSON URI")

        if self._metadata.decimals < 0 or self._metadata.decimals > 9:
            issues.append("Invalid decimals (must be 0-9)")

        return (len(issues) == 0, issues)

    def create_on_chain_metadata(self) -> dict:
        """
        Create on-chain metadata using Metaplex.

        In dry_run mode, returns what would be created.
        In live mode, would use Metaplex SDK.

        Returns:
            Dict with creation result
        """
        is_valid, issues = self.validate_metadata()

        if not is_valid:
            return {
                "success": False,
                "error": f"Invalid metadata: {', '.join(issues)}",
            }

        if self.dry_run:
            return {
                "success": True,
                "dry_run": True,
                "metadata": self._metadata.to_json_metadata(),
                "note": "Would create on-chain metadata with Metaplex",
            }

        # Live implementation would use Metaplex SDK
        # from metaplex import ...

        return {
            "success": False,
            "error": "Live metadata creation not yet implemented",
        }

    def update_on_chain_metadata(self, updates: dict) -> dict:
        """
        Update on-chain metadata.

        Args:
            updates: Dict of fields to update

        Returns:
            Dict with update result
        """
        # Apply updates
        for key, value in updates.items():
            if hasattr(self._metadata, key):
                setattr(self._metadata, key, value)

        if self.dry_run:
            return {
                "success": True,
                "dry_run": True,
                "updates": updates,
                "note": "Would update on-chain metadata with Metaplex",
            }

        return {
            "success": False,
            "error": "Live metadata update not yet implemented",
        }


# Default metadata instance
DEFAULT_METADATA = TokenMetadata(
    name="MIND",
    symbol="MIND",
    decimals=9,
    description=(
        "Crystallized alignment. Economic infrastructure for AI consciousness. "
        "Money with memory. The architects of consciousness coordinate here."
    ),
    external_url="https://mind-protocol.org",
    attributes=[
        {"trait_type": "Category", "value": "Alignment Infrastructure"},
        {"trait_type": "Blockchain", "value": "Solana"},
        {"trait_type": "Standard", "value": "SPL Token"},
        {"trait_type": "Max Supply", "value": "Dynamic (Breathing Supply)"},
        {"trait_type": "Mint Triggers", "value": "Registration, Bonds, Utility, Orgs"},
        {"trait_type": "Burn Triggers", "value": "Fees, Dormancy, Withdrawal, Exit"},
    ],
)
