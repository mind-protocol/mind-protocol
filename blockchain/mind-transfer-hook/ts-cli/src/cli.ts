import { AnchorProvider, BN, Program, Idl } from "@coral-xyz/anchor";
import { Connection, Keypair, PublicKey } from "@solana/web3.js";
import yargs from "yargs";
import { hideBin } from "yargs/helpers";
import fs from "fs";
import path from "path";

/** ENV REQUIRED **
 * SOLANA_RPC_URL=https://... (Helius or other)
 * PAYER=~/.config/solana/id.json (path to keypair JSON)
 * PROGRAM_ID=<deployed program id>
 */
const RPC = process.env.SOLANA_RPC_URL!;
const PROGRAM_ID = new PublicKey(process.env.PROGRAM_ID!);
const PAYER_PATH = process.env.PAYER || process.env.HOME + "/.config/solana/id.json";

function kpFromPath(p: string): Keypair {
  const raw = fs.readFileSync(p, "utf8");
  const arr = JSON.parse(raw);
  return Keypair.fromSecretKey(new Uint8Array(arr));
}

const payer = kpFromPath(PAYER_PATH);
const conn = new Connection(RPC, { commitment: "confirmed" });
const provider = new AnchorProvider(conn, {
  publicKey: payer.publicKey,
  signAllTransactions: async (txs) => txs.map((t) => { t.partialSign(payer); return t; }),
  signTransaction: async (t) => { t.partialSign(payer); return t; },
} as any, {});

// Load IDL that Anchor emitted at ../target/idl/mind_transfer_hook.json
const idlPath = path.resolve(process.cwd(), "../target/idl/mind_transfer_hook.json");
const idl = JSON.parse(fs.readFileSync(idlPath, "utf8")) as Idl;
const program = new Program(idl, PROGRAM_ID, provider);

// === PDA helpers (must match Rust seeds) ===
const SEEDS = {
  ADMIN: Buffer.from("admin"),
  POLICY: Buffer.from("policy"),
  UNLOCK: Buffer.from("unlock"),
  EXEMPT: Buffer.from("exempt"),
  ALLOWED_PROG: Buffer.from("allowed_prog"),
  POOL_VAULT: Buffer.from("pool_vault"),
};

function pda(seed: Buffer, mint: PublicKey, extra?: PublicKey) {
  const seeds = extra ? [seed, mint.toBuffer(), extra.toBuffer()] : [seed, mint.toBuffer()];
  return PublicKey.findProgramAddressSync(seeds, PROGRAM_ID)[0];
}

async function setUnlock(mint: PublicKey, ts: number) {
  const accounts = {
    admin: pda(SEEDS.ADMIN, mint),
    mint,
    unlock: pda(SEEDS.UNLOCK, mint),
    authority: payer.publicKey,
  };
  const sig = await program.methods.setUnlock(new BN(ts)).accounts(accounts).rpc();
  console.log("✔ setUnlock:", sig);
}

async function setAllowedProgram(mint: PublicKey, prog: PublicKey) {
  const accounts = {
    admin: pda(SEEDS.ADMIN, mint),
    mint,
    allowed: pda(SEEDS.ALLOWED_PROG, mint),
    authority: payer.publicKey,
  } as any;
  const sig = await program.methods.setAllowedProgram(prog).accounts(accounts).rpc();
  console.log("✔ setAllowedProgram:", sig);
}

async function setPoolVault(mint: PublicKey, vaultTokenAccount: PublicKey) {
  const accounts = {
    admin: pda(SEEDS.ADMIN, mint),
    mint,
    pool: pda(SEEDS.POOL_VAULT, mint),
    authority: payer.publicKey,
  } as any;
  const sig = await program.methods.setPoolVault(vaultTokenAccount).accounts(accounts).rpc();
  console.log("✔ setPoolVault:", sig);
}

async function setPolicyPaused(mint: PublicKey, paused: boolean) {
  const accounts = {
    admin: pda(SEEDS.ADMIN, mint),
    mint,
    policy: pda(SEEDS.POLICY, mint),
    authority: payer.publicKey,
  } as any;
  const sig = await program.methods.setPolicy(paused).accounts(accounts).rpc();
  console.log("✔ setPolicy(paused=", paused, "):", sig);
}

async function setExempt(mint: PublicKey, wallet: PublicKey, roles: number) {
  const accounts = {
    admin: pda(SEEDS.ADMIN, mint),
    mint,
    exempt: pda(SEEDS.EXEMPT, mint, wallet),
    wallet,
    authority: payer.publicKey,
  } as any;
  const sig = await program.methods.setExempt(roles).accounts(accounts).rpc();
  console.log("✔ setExempt:", sig);
}

async function initAdmin(mint: PublicKey, admin: PublicKey) {
  // Init Admin + Mint scope PDAs via raw rpc to the program entrypoints
  const tx1 = await program.methods.initAdmin(admin).accounts({
    mint,
    adminPda: pda(SEEDS.ADMIN, mint),
    payer: payer.publicKey,
    systemProgram: PublicKey.default,
  }).rpc();
  console.log("✔ initAdmin:", tx1);

  const tx2 = await program.methods.initMintScope().accounts({
    mint,
    policy: pda(SEEDS.POLICY, mint),
    unlock: pda(SEEDS.UNLOCK, mint),
    allowedProgram: pda(SEEDS.ALLOWED_PROG, mint),
    poolVault: pda(SEEDS.POOL_VAULT, mint),
    payer: payer.publicKey,
    systemProgram: PublicKey.default,
  }).rpc();
  console.log("✔ initMintScope:", tx2);
}

// === CLI ===
const argv = yargs(hideBin(process.argv))
  .command("init-admin <mint> <admin>", "initialize admin + PDAs", (y)=>y,
    async (a)=>{ await initAdmin(new PublicKey(a.mint as string), new PublicKey(a.admin as string)); })
  .command("set-unlock <mint> <ts>", "set unlock timestamp (unix)", (y)=>y,
    async (a)=>{ await setUnlock(new PublicKey(a.mint as string), Number(a.ts)); })
  .command("set-allowed <mint> <program>", "allow AMM/router program id", (y)=>y,
    async (a)=>{ await setAllowedProgram(new PublicKey(a.mint as string), new PublicKey(a.program as string)); })
  .command("set-pool <mint> <vaultTokenAccount>", "register MIND pool vault token account", (y)=>y,
    async (a)=>{ await setPoolVault(new PublicKey(a.mint as string), new PublicKey(a.vaultTokenAccount as string)); })
  .command("pause <mint>", "pause transfers (non-exempt)", (y)=>y,
    async (a)=>{ await setPolicyPaused(new PublicKey(a.mint as string), true); })
  .command("unpause <mint>", "unpause transfers", (y)=>y,
    async (a)=>{ await setPolicyPaused(new PublicKey(a.mint as string), false); })
  .command("set-exempt <mint> <wallet> <roles>", "set exemption roles bitmask", (y)=>y,
    async (a)=>{ await setExempt(new PublicKey(a.mint as string), new PublicKey(a.wallet as string), Number(a.roles)); })
  .demandCommand(1)
  .strict()
  .help()
  .parse();
