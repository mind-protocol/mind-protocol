// create_mind_token.ts
//
// $MIND Token Creation — SPL Token 2022 with Extensions
// Mainnet deployment — IRREVERSIBLE once executed
//
// Extensions:
// - TransferFeeConfig (1% baseline)
// - TransferHook (custom logic on each transfer)
// - MetadataPointer (self-referencing)
// - TokenMetadata (name, symbol, URI on-chain)
// - MintCloseAuthority
//
// Freeze Authority: null (censorship resistant)
//
// Run: npx ts-node create_mind_token.ts

import {
  Connection,
  Keypair,
  SystemProgram,
  Transaction,
  PublicKey,
  sendAndConfirmTransaction,
} from "@solana/web3.js";
import {
  TOKEN_2022_PROGRAM_ID,
  ExtensionType,
  createInitializeMintInstruction,
  createInitializeTransferFeeConfigInstruction,
  createInitializeTransferHookInstruction,
  createInitializeMetadataPointerInstruction,
  getMintLen,
  createInitializeMintCloseAuthorityInstruction,
} from "@solana/spl-token";
import {
  createInitializeInstruction as createInitializeMetadataInstruction,
} from "@solana/spl-token-metadata";
import * as fs from "fs";

const RPC_URL = "https://api.mainnet-beta.solana.com";
const TRANSFER_HOOK_PROGRAM_ID = new PublicKey("325JiLH2czH47tnDzheS6rQdDh9rHa1mD8wVuRUPDAnD");

// Token properties
const TOKEN_NAME = "MIND";
const TOKEN_SYMBOL = "MIND";
const TOKEN_URI = "https://mind-protocol.org/token-metadata.json";
const TOKEN_DECIMALS = 9;
const TRANSFER_FEE_BASIS_POINTS = 100; // 1%
const TRANSFER_FEE_MAX = BigInt(1_000_000_000); // 1 MIND max fee

async function createMindToken() {
  console.log("==================================================");
  console.log("  $MIND Token Creation — Solana Mainnet");
  console.log("==================================================");

  const connection = new Connection(RPC_URL, "confirmed");

  // Load payer keypair
  const keypairPath = process.env.HOME + "/.config/solana/id.json";
  console.log(`  Keypair: ${keypairPath}`);
  const payerKeypair = Keypair.fromSecretKey(
    Uint8Array.from(JSON.parse(fs.readFileSync(keypairPath).toString()))
  );
  console.log(`  Payer: ${payerKeypair.publicKey.toString()}`);

  // Generate mint keypair
  const mintKeypair = Keypair.generate();
  console.log(`  Mint address: ${mintKeypair.publicKey.toString()}`);

  // Calculate mint account size with extensions
  const extensions = [
    ExtensionType.TransferFeeConfig,
    ExtensionType.TransferHook,
    ExtensionType.MetadataPointer,
    ExtensionType.MintCloseAuthority,
  ];
  const mintLen = getMintLen(extensions) + 512; // Extra space for metadata
  console.log(`  Mint account size: ${mintLen} bytes`);

  // Get rent exemption
  const lamports = await connection.getMinimumBalanceForRentExemption(mintLen);
  console.log(`  Rent exemption: ${lamports / 1e9} SOL`);

  // Check balance
  const balance = await connection.getBalance(payerKeypair.publicKey);
  console.log(`  Balance: ${balance / 1e9} SOL`);
  if (balance < lamports + 10_000) {
    throw new Error(`Insufficient balance: ${balance / 1e9} SOL (need ~${lamports / 1e9} SOL)`);
  }

  console.log("");
  console.log("  Building transaction...");

  // 1. Create account instruction
  const createAccountIx = SystemProgram.createAccount({
    fromPubkey: payerKeypair.publicKey,
    newAccountPubkey: mintKeypair.publicKey,
    space: mintLen,
    lamports,
    programId: TOKEN_2022_PROGRAM_ID,
  });

  // 2. Initialize TransferFeeConfig
  const initTransferFeeIx = createInitializeTransferFeeConfigInstruction(
    mintKeypair.publicKey,
    payerKeypair.publicKey,  // transferFeeAuthority
    payerKeypair.publicKey,  // withdrawWithheldAuthority
    TRANSFER_FEE_BASIS_POINTS,
    TRANSFER_FEE_MAX,
    TOKEN_2022_PROGRAM_ID
  );

  // 3. Initialize TransferHook
  const initTransferHookIx = createInitializeTransferHookInstruction(
    mintKeypair.publicKey,
    payerKeypair.publicKey,  // transferHookAuthority
    TRANSFER_HOOK_PROGRAM_ID,
    TOKEN_2022_PROGRAM_ID
  );

  // 4. Initialize MetadataPointer (self-referencing — metadata stored in mint)
  const initMetadataPointerIx = createInitializeMetadataPointerInstruction(
    mintKeypair.publicKey,
    payerKeypair.publicKey,  // metadataAuthority
    mintKeypair.publicKey,   // metadata account = mint itself
    TOKEN_2022_PROGRAM_ID
  );

  // 5. Initialize MintCloseAuthority
  const initMintCloseIx = createInitializeMintCloseAuthorityInstruction(
    mintKeypair.publicKey,
    payerKeypair.publicKey,  // mintCloseAuthority
    TOKEN_2022_PROGRAM_ID
  );

  // 6. Initialize Mint
  const initMintIx = createInitializeMintInstruction(
    mintKeypair.publicKey,
    TOKEN_DECIMALS,
    payerKeypair.publicKey,  // mintAuthority
    null,                     // freezeAuthority = null (CENSORSHIP RESISTANT)
    TOKEN_2022_PROGRAM_ID
  );

  // 7. Initialize TokenMetadata
  const initMetadataIx = createInitializeMetadataInstruction({
    programId: TOKEN_2022_PROGRAM_ID,
    mint: mintKeypair.publicKey,
    metadata: mintKeypair.publicKey,
    mintAuthority: payerKeypair.publicKey,
    name: TOKEN_NAME,
    symbol: TOKEN_SYMBOL,
    uri: TOKEN_URI,
    updateAuthority: payerKeypair.publicKey,
  });

  // Build transaction — ORDER MATTERS
  // Extensions MUST be initialized BEFORE the mint
  const tx = new Transaction().add(
    createAccountIx,
    initTransferFeeIx,
    initTransferHookIx,
    initMetadataPointerIx,
    initMintCloseIx,
    initMintIx,
    initMetadataIx
  );

  console.log("  Sending transaction...");

  // Send and confirm
  const signature = await sendAndConfirmTransaction(
    connection,
    tx,
    [payerKeypair, mintKeypair],
    { commitment: "finalized" }
  );

  console.log("");
  console.log("==================================================");
  console.log("  $MIND TOKEN CREATED SUCCESSFULLY");
  console.log("==================================================");
  console.log(`  Mint Address: ${mintKeypair.publicKey.toString()}`);
  console.log(`  Transaction:  ${signature}`);
  console.log(`  Network:      mainnet-beta`);
  console.log(`  Decimals:     ${TOKEN_DECIMALS}`);
  console.log(`  Transfer Fee: ${TRANSFER_FEE_BASIS_POINTS} bps (1%)`);
  console.log(`  TransferHook: ${TRANSFER_HOOK_PROGRAM_ID.toString()}`);
  console.log(`  Freeze Auth:  null (censorship resistant)`);
  console.log("==================================================");

  // Save mint info
  const mintInfo = {
    mint: mintKeypair.publicKey.toString(),
    network: "mainnet-beta",
    signature,
    payer: payerKeypair.publicKey.toString(),
    transferHookProgram: TRANSFER_HOOK_PROGRAM_ID.toString(),
    extensions: [
      "TransferFeeConfig",
      "TransferHook",
      "MetadataPointer",
      "TokenMetadata",
      "MintCloseAuthority",
    ],
    metadata: {
      name: TOKEN_NAME,
      symbol: TOKEN_SYMBOL,
      uri: TOKEN_URI,
      decimals: TOKEN_DECIMALS,
    },
    fees: {
      transferFeeBasisPoints: TRANSFER_FEE_BASIS_POINTS,
      maxFee: TRANSFER_FEE_MAX.toString(),
    },
    freezeAuthority: null,
    createdAt: new Date().toISOString(),
  };

  fs.writeFileSync("mind_token_mint.json", JSON.stringify(mintInfo, null, 2));
  console.log("\n  Saved to mind_token_mint.json");

  // Also save the mint keypair (BACKUP — needed for reference)
  fs.writeFileSync(
    "mind_token_mint_keypair.json",
    JSON.stringify(Array.from(mintKeypair.secretKey))
  );
  console.log("  Saved mint keypair to mind_token_mint_keypair.json");
}

createMindToken().catch((err) => {
  console.error("FAILED:", err.message);
  process.exit(1);
});
