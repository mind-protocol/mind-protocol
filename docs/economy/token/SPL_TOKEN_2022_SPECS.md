# SPL Token 2022 — Spécifications Critiques

```
PRIORITY: CRITICAL
TIMING: Doit être appliqué AVANT création du token
RAISON: Extensions ne peuvent PAS être ajoutées après initialisation
```

---

## TL;DR

**Utilise `TOKEN_2022_PROGRAM_ID`, pas `TOKEN_PROGRAM_ID`.**

Les extensions doivent être déclarées à la création du mint. Impossible de les ajouter après.

---

## Extensions À Activer

| Extension | Purpose | Config |
|-----------|---------|--------|
| **TransferFeeConfig** | Membrane fees automatiques | fee_basis_points: 100-500 (1-5%), max_fee: configurable |
| **TransferHook** | Logic custom sur chaque transfer | program_id: notre transfer hook program |
| **MetadataPointer** | Pointe vers metadata | self-referencing (metadata dans le mint) |
| **TokenMetadata** | Name, symbol, URI on-chain | name: "MIND", symbol: "MIND", uri: metadata JSON |
| **MintCloseAuthority** | Option de fermer le mint | authority: protocol multisig |

---

## Extensions À NE PAS Activer

| Extension | Pourquoi Non |
|-----------|--------------|
| **PermanentDelegate** | Trop de pouvoir centralisé — peut transfer/burn tout |
| **NonTransferable** | On veut des transfers |
| **DefaultAccountState** | Pas de freeze par défaut |
| **ConfidentialTransfer** | Transparence OK, pas besoin de privacy |
| **InterestBearing** | Pas notre modèle économique |

---

## Décision: PermanentDelegate

**On n'active PAS PermanentDelegate.**

Raisons:
- Donne accès illimité à TOUS les token accounts
- Si compromis → catastrophe totale
- Trust issue pour holders externes
- Les citoyens géreront leurs propres wallets
- TransferHook suffit pour la logique custom

Alternative pour comptes dormants:
- Dormancy = pas de transfers entrants autorisés (via TransferHook)
- Owner doit réactiver son compte
- Pas de confiscation automatique

---

## Code: Création du Token

```typescript
import {
  TOKEN_2022_PROGRAM_ID,
  ExtensionType,
  createInitializeMintInstruction,
  createInitializeTransferFeeConfigInstruction,
  createInitializeTransferHookInstruction,
  createInitializeMetadataPointerInstruction,
  getMintLen,
} from "@solana/spl-token";
import {
  createInitializeInstruction as createInitializeMetadataInstruction,
} from "@solana/spl-token-metadata";

// 1. Calculer la taille du mint avec extensions
const extensions = [
  ExtensionType.TransferFeeConfig,
  ExtensionType.TransferHook,
  ExtensionType.MetadataPointer,
];
const mintLen = getMintLen(extensions);

// 2. Créer le compte mint
const mintKeypair = Keypair.generate();
const createAccountIx = SystemProgram.createAccount({
  fromPubkey: payer.publicKey,
  newAccountPubkey: mintKeypair.publicKey,
  space: mintLen,
  lamports: await connection.getMinimumBalanceForRentExemption(mintLen),
  programId: TOKEN_2022_PROGRAM_ID,  // <-- CRITICAL: Token 2022
});

// 3. Initialiser TransferFeeConfig
const initTransferFeeIx = createInitializeTransferFeeConfigInstruction(
  mintKeypair.publicKey,
  transferFeeAuthority.publicKey,    // Qui peut changer les fees
  withdrawWithheldAuthority.publicKey, // Qui peut récupérer les fees
  100,  // feeBasisPoints: 100 = 1%
  BigInt(1_000_000_000),  // maxFee: 1 MIND max per transfer
  TOKEN_2022_PROGRAM_ID,
);

// 4. Initialiser TransferHook
const initTransferHookIx = createInitializeTransferHookInstruction(
  mintKeypair.publicKey,
  transferHookAuthority.publicKey,   // Qui peut changer le hook program
  transferHookProgramId,              // Le program qui gère la logique
  TOKEN_2022_PROGRAM_ID,
);

// 5. Initialiser MetadataPointer (self-referencing)
const initMetadataPointerIx = createInitializeMetadataPointerInstruction(
  mintKeypair.publicKey,
  metadataAuthority.publicKey,
  mintKeypair.publicKey,  // Metadata stockée dans le mint lui-même
  TOKEN_2022_PROGRAM_ID,
);

// 6. Initialiser le Mint
const initMintIx = createInitializeMintInstruction(
  mintKeypair.publicKey,
  9,  // decimals
  mintAuthority.publicKey,
  null,  // freezeAuthority: null = pas de freeze
  TOKEN_2022_PROGRAM_ID,
);

// 7. Ajouter Metadata
const initMetadataIx = createInitializeMetadataInstruction({
  programId: TOKEN_2022_PROGRAM_ID,
  mint: mintKeypair.publicKey,
  metadata: mintKeypair.publicKey,
  mintAuthority: mintAuthority.publicKey,
  name: "MIND",
  symbol: "MIND",
  uri: "https://mind-protocol.io/token-metadata.json",
  updateAuthority: metadataAuthority.publicKey,
});

// 8. Transaction
const tx = new Transaction().add(
  createAccountIx,
  initTransferFeeIx,
  initTransferHookIx,
  initMetadataPointerIx,
  initMintIx,
  initMetadataIx,
);
```

---

## Authorities à Définir

| Authority | Rôle | Initial | Long-term |
|-----------|------|---------|-----------|
| **mintAuthority** | Peut minter des tokens | Single wallet | Multi-sig |
| **freezeAuthority** | Peut freeze des accounts | `null` (disabled) | - |
| **transferFeeAuthority** | Peut changer le fee % | Protocol wallet | Multi-sig |
| **withdrawWithheldAuthority** | Peut collecter les fees | Protocol treasury | Multi-sig |
| **transferHookAuthority** | Peut changer le hook program | Protocol wallet | Multi-sig |
| **metadataAuthority** | Peut update metadata | Protocol wallet | Multi-sig |

**Note:** On désactive `freezeAuthority` (null) pour censorship resistance.

---

## TransferHook Program

Le TransferHook permet d'exécuter de la logique custom à chaque transfer. 

**Use cases pour $MIND:**
- Vérifier que sender n'est pas dormant
- Logger le transfer pour trust score calculation
- Vérifier limites de transfer (rate limiting)
- Bloquer transfers vers addresses blacklistées (si nécessaire)

**Structure du program:**
```rust
// transfer_hook/src/lib.rs
use anchor_lang::prelude::*;
use spl_transfer_hook_interface::instruction::ExecuteInstruction;

#[program]
pub mod mind_transfer_hook {
    use super::*;

    pub fn transfer_hook(ctx: Context<TransferHook>, amount: u64) -> Result<()> {
        // 1. Check sender not dormant
        // 2. Update transfer counter for sender/receiver
        // 3. Emit event for off-chain indexing
        
        msg!("MIND transfer: {} tokens", amount);
        Ok(())
    }
}

#[derive(Accounts)]
pub struct TransferHook<'info> {
    #[account(token::mint = mint)]
    pub source: InterfaceAccount<'info, TokenAccount>,
    pub mint: InterfaceAccount<'info, Mint>,
    #[account(token::mint = mint)]
    pub destination: InterfaceAccount<'info, TokenAccount>,
    pub owner: UncheckedAccount<'info>,
    /// CHECK: Extra account for hook logic
    pub extra_account_metas: UncheckedAccount<'info>,
}
```

**Note:** Le TransferHook program doit être déployé AVANT de créer le token.

---

## TransferFee: Comment Ça Marche

1. À chaque transfer, `fee = min(amount * feeBasisPoints / 10000, maxFee)`
2. Le fee est retenu ("withheld") dans le destination token account
3. Protocol peut collecter les fees via `withdrawWithheldTokensFromAccounts`
4. Ou `harvestWithheldTokensToMint` pour centraliser dans le mint

**Membrane fees via TransferFee:**
- L1 → L2: 1% (feeBasisPoints = 100)
- L2 → L3: 2% (feeBasisPoints = 200)  
- L3 → L4: 3% (feeBasisPoints = 300)

**Challenge:** Un seul feeBasisPoints par token.

**Solution:** Layer fees dans le TransferHook program, pas TransferFee.
- TransferFee = 1% baseline (protocol fee)
- TransferHook = calcule layer difference, exécute transfer supplémentaire

---

## Fichiers À Créer/Modifier

```
economy/token/
├── spl_token_2022_mint_creator.py          # Création du token avec extensions
├── token_mint_authority_controller.py       # Gestion mint authority
├── token_burn_condition_executor.py         # Burn logic
├── metaplex_token_metadata_manager.py       # Metadata management
├── token_supply_target_calculator.py        # Supply formulas
├── token_solana_deployment_script.py        # Deploy script
├── transfer_fee_collector.py                # Collect withheld fees
└── constants.py                             # Program IDs, decimals, etc.

programs/transfer_hook/                       # Anchor program (Rust)
├── src/
│   └── lib.rs
├── Cargo.toml
└── Anchor.toml
```

---

## Validation Checklist

Avant de déployer, vérifier:

- [ ] Token créé avec `TOKEN_2022_PROGRAM_ID`
- [ ] Extension `TransferFeeConfig` activée
- [ ] Extension `TransferHook` activée avec bon program ID
- [ ] Extension `MetadataPointer` activée
- [ ] `freezeAuthority` est `null`
- [ ] Metadata (name, symbol, uri) correcte
- [ ] TransferHook program déployé et testé
- [ ] Toutes les authorities documentées et sécurisées

---

## Prochaines Étapes

1. **Créer le TransferHook program** (Anchor/Rust)
2. **Déployer TransferHook sur devnet** pour tests
3. **Créer le token avec extensions** pointant vers TransferHook
4. **Tester transfers** — vérifier que hook s'exécute
5. **Tester fee collection** — vérifier que fees sont collectées
6. **Déployer sur mainnet** quand tout validé

---

## Questions Ouvertes

1. **Layer-based fees:** Comment encoder le layer d'un account? Options:
   - PDA avec metadata
   - Lookup table maintenu par protocol
   - Account tag dans extra_account_metas

2. **TransferHook program upgrade:** Garder upgradeable ou freeze après audit?

3. **Fee withdrawal frequency:** À chaque block? Daily? Weekly?

---

*"Les extensions sont le moment de vérité. Une fois créé, le token garde cette forme pour toujours."*
