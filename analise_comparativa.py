#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analise Comparativa - Reproducao da Tabela 2 do artigo

Compara dois metodos para o Samsung Galaxy A35 5G:
  1. Extracao Direta: polaridades medias a partir das avaliacoes do proprio produto alvo
  2. PKG Enriquecido: polaridades inferidas pela media aritmetica das opinioes de
     produtos similares que compartilham o mesmo atributo tecnico no PKG

Metricas:
  - Concordancia de polaridade (mesmo sinal) por categoria
  - MAE (erro absoluto medio) das nove categorias
"""

import pandas as pd

# ============================================================================
# 1. CARREGAMENTO DOS DADOS DE OPINIOES EXTRAIDAS PELO SABIA-3.1
# ============================================================================

df1 = pd.read_excel("avaliacoes_opinioes.xlsx")
df2 = pd.read_excel("avaliacoes_opinioes_2.xlsx")
df3 = pd.read_excel("avaliacoes_opinioes_3.xlsx")

combined_df = pd.concat([df1, df2, df3], ignore_index=True)

print(f"Total de tuplas de opiniao: {len(combined_df)}")
print(f"Celulares: {sorted(combined_df['celular'].unique().tolist())}")
print(f"Categorias: {sorted(combined_df['categoria'].unique().tolist())}")

# ============================================================================
# 2. SEPARACAO: EXTRACAO DIRETA vs ENRIQUECIMENTO PKG
# ============================================================================

target_phone = "Samsung Galaxy A35 5G"

# Metodo 1: Extracao Direta (opinioes do proprio produto alvo)
target_opinions = combined_df[combined_df["celular"] == target_phone]

# Metodo 2: Enriquecimento PKG (opinioes dos 5 produtos similares)
enrichment_opinions = combined_df[combined_df["celular"] != target_phone]

print(f"\nExtracao Direta ({target_phone}): {len(target_opinions)} opinioes")
print(f"Enriquecimento PKG (similares): {len(enrichment_opinions)} opinioes")

# ============================================================================
# 3. CALCULO DAS POLARIDADES MEDIAS POR CATEGORIA
# ============================================================================

categories = sorted(combined_df["categoria"].unique())

print("\n" + "=" * 85)
print("TABELA 2 - Comparacao por categoria")
print("=" * 85)
print(
    f"{'Categoria':<22} {'N_dir':>6} {'Pol.Media':>10} "
    f"{'N_enr':>7} {'Pol.Media':>10} {'Dif.Abs.':>9} {'Concordancia':>13}"
)
print("-" * 85)

total_diff = 0.0
concordance_count = 0

for cat in categories:
    t = target_opinions[target_opinions["categoria"] == cat]
    e = enrichment_opinions[enrichment_opinions["categoria"] == cat]

    pol_t = t["polaridade"].mean()
    pol_e = e["polaridade"].mean()
    diff = abs(pol_t - pol_e)

    # Concordancia: ambos positivos ou ambos negativos
    concordant = (pol_t >= 0 and pol_e >= 0) or (pol_t < 0 and pol_e < 0)
    conc_label = "Sim" if concordant else "Nao"
    if concordant:
        concordance_count += 1

    total_diff += diff

    print(
        f"{cat:<22} {len(t):>6} {pol_t:>+10.3f} "
        f"{len(e):>7} {pol_e:>+10.3f} {diff:>9.3f} {conc_label:>13}"
    )

mae = total_diff / len(categories)

print("-" * 85)
print(
    f"{'Total':<22} {len(target_opinions):>6} {'':>10} "
    f"{len(enrichment_opinions):>7} {'':>10} {mae:>9.3f} "
    f"{concordance_count}/{len(categories):>11}"
)

# ============================================================================
# 4. RESUMO
# ============================================================================

print("\n" + "=" * 85)
print("METRICAS FINAIS")
print("=" * 85)
print(f"  MAE (erro absoluto medio): {mae:.3f}")
print(f"  Concordancia de polaridade: {concordance_count}/{len(categories)} ({100*concordance_count/len(categories):.1f}%)")
