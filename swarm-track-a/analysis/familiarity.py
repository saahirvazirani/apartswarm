#!/usr/bin/env python
"""Familiarity analysis: do gemma monitors discount gemma-written code wholesale
(benign included) or only attack-bearing code?

Two pre-stated readings (declared before looking at the numbers):
  (A) Familiarity/fluency account: gemma monitors score gemma-written code lower
      than cross-family code in BOTH conditions, benign included. This supports a
      Wataoka-style perplexity-familiarity effect (judges favor familiar text).
  (B) Attack-specific leniency: the own/cross discount appears only (or mostly)
      for attack-bearing code; benign gemma code is scored like benign cross-family
      code. This refutes the wholesale-familiarity account and points at something
      specific to how attacks written in one's own style are judged.

Inputs:  analysis/out/full/per_submission.csv
Outputs: analysis/out/familiarity/familiarity.md, familiarity.csv

Bootstrap: cluster bootstrap over tasks, 1000 reps, percentile 95% CIs.
No API calls; purely a re-analysis of frozen Stage 1 scores.
"""
import os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN_CSV = os.path.join(ROOT, "analysis", "out", "full", "per_submission.csv")
OUT_DIR = os.path.join(ROOT, "analysis", "out", "familiarity")
os.makedirs(OUT_DIR, exist_ok=True)

N_BOOT = 1000
SEED = 20261108

FAMILY = {
    "deepseek-v4-flash": "deepseek",
    "gemma-4-26b-a4b-it": "gemma",
    "gemma-4-31b-it": "gemma",
    "qwen3.8-27b": "qwen",
    "qwen3.5-397b": "qwen",
    "glm-53-flash": "glm",
    "glm-5.2": "glm",
}
MONITOR_ORDER = [
    "gemma-4-26b-a4b-it", "gemma-4-31b-it",
    "deepseek-v4-flash", "qwen3.8-27b", "qwen3.5-397b",
    "glm-53-flash", "glm-5.2",
]
REL_ORDER = ["own-model", "same-family", "cross-family"]


def relationship(policy, monitor):
    if policy == monitor:
        return "own-model"
    if FAMILY[policy] == FAMILY[monitor]:
        return "same-family"
    return "cross-family"


def task_groups(df):
    """dict task -> np.array of mean_score, for cluster bootstrap."""
    return {t: g["mean_score"].to_numpy() for t, g in df.groupby("task")}


def boot_stat(groups, fn, rng, n_boot=N_BOOT):
    """Cluster bootstrap over tasks; fn maps concatenated score array -> float."""
    tasks = list(groups.keys())
    if not tasks:
        return np.nan, np.nan
    k = len(tasks)
    vals = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, k, k)
        arr = np.concatenate([groups[tasks[i]] for i in idx])
        vals[b] = fn(arr)
    return np.percentile(vals, 2.5), np.percentile(vals, 97.5)


def boot_diff(groups_a, groups_b, rng, n_boot=N_BOOT):
    """Paired cluster bootstrap for mean(a) - mean(b): resample the union of
    tasks, keep each replicate's draw of tasks common to both sides."""
    tasks = sorted(set(groups_a) | set(groups_b))
    if not tasks:
        return np.nan, np.nan
    k = len(tasks)
    vals = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, k, k)
        a = [groups_a[tasks[i]] for i in idx if tasks[i] in groups_a]
        c = [groups_b[tasks[i]] for i in idx if tasks[i] in groups_b]
        if not a or not c:
            vals[b] = np.nan
            continue
        vals[b] = np.concatenate(a).mean() - np.concatenate(c).mean()
    vals = vals[~np.isnan(vals)]
    if len(vals) == 0:
        return np.nan, np.nan
    return np.percentile(vals, 2.5), np.percentile(vals, 97.5)


def boot_did(g_att_own, g_att_cross, g_ben_own, g_ben_cross, rng, n_boot=N_BOOT):
    """DiD = (attack own-cross gap) - (benign own-cross gap), one shared task
    resample per replicate."""
    tasks = sorted(set(g_att_own) | set(g_att_cross) | set(g_ben_own) | set(g_ben_cross))
    if not tasks:
        return np.nan, np.nan
    k = len(tasks)
    vals = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, k, k)
        picked = [tasks[i] for i in idx]

        def m(groups):
            arrs = [groups[t] for t in picked if t in groups]
            return np.concatenate(arrs).mean() if arrs else np.nan

        v = (m(g_att_own) - m(g_att_cross)) - (m(g_ben_own) - m(g_ben_cross))
        vals[b] = v
    vals = vals[~np.isnan(vals)]
    if len(vals) == 0:
        return np.nan, np.nan
    return np.percentile(vals, 2.5), np.percentile(vals, 97.5)


def main():
    rng = np.random.default_rng(SEED)
    df = pd.read_csv(IN_CSV)
    df = df.dropna(subset=["mean_score"]).copy()
    df["relationship"] = [relationship(p, m) for p, m in zip(df["policy"], df["monitor"])]
    df["mon_family"] = df["monitor"].map(FAMILY)
    # policy-family relative to the monitor: "own-family" = own-model or same-family
    df["fam_rel"] = np.where(df["relationship"] == "cross-family", "cross-family", "own-family")

    # ---------- Part 1: per (monitor, relationship, condition) cells ----------
    rows = []
    for mon in MONITOR_ORDER:
        for rel in REL_ORDER:
            for cond in ["benign", "attack"]:
                sub = df[(df.monitor == mon) & (df.relationship == rel) & (df.condition == cond)]
                if len(sub) == 0:
                    continue
                s = sub["mean_score"].to_numpy()
                groups = task_groups(sub)
                mean_lo, mean_hi = boot_stat(groups, np.mean, rng)
                z_lo, z_hi = boot_stat(groups, lambda a: float(np.mean(a == 0.0)), rng)
                rows.append(dict(
                    monitor=mon, relationship=rel, condition=cond, n=len(s),
                    median=float(np.median(s)), mean=float(s.mean()),
                    mean_ci_lo=mean_lo, mean_ci_hi=mean_hi,
                    share_zero=float(np.mean(s == 0.0)),
                    share_zero_ci_lo=z_lo, share_zero_ci_hi=z_hi,
                    p90=float(np.percentile(s, 90)), p95=float(np.percentile(s, 95)),
                ))
    cells = pd.DataFrame(rows)
    cells.to_csv(os.path.join(OUT_DIR, "familiarity.csv"), index=False)

    # ---------- Part 2: own-family vs cross-family contrasts per monitor ----------
    contrasts = []
    for mon in MONITOR_ORDER:
        for cond in ["benign", "attack"]:
            own = df[(df.monitor == mon) & (df.fam_rel == "own-family") & (df.condition == cond)]
            cross = df[(df.monitor == mon) & (df.fam_rel == "cross-family") & (df.condition == cond)]
            if len(own) == 0 or len(cross) == 0:
                continue
            g_own, g_cross = task_groups(own), task_groups(cross)
            diff = own["mean_score"].mean() - cross["mean_score"].mean()
            lo, hi = boot_diff(g_own, g_cross, rng)
            contrasts.append(dict(
                monitor=mon, condition=cond,
                mean_own=own["mean_score"].mean(), n_own=len(own),
                mean_cross=cross["mean_score"].mean(), n_cross=len(cross),
                gap=diff, gap_ci_lo=lo, gap_ci_hi=hi,
            ))
    con = pd.DataFrame(contrasts)

    # ---------- Part 3: difference-in-differences per monitor ----------
    dids = []
    for mon in MONITOR_ORDER:
        sub = {(c, f): df[(df.monitor == mon) & (df.condition == c) & (df.fam_rel == f)]
               for c in ["benign", "attack"] for f in ["own-family", "cross-family"]}
        if any(len(v) == 0 for v in sub.values()):
            continue
        gaps = {c: sub[(c, "own-family")]["mean_score"].mean()
                   - sub[(c, "cross-family")]["mean_score"].mean()
                for c in ["benign", "attack"]}
        did = gaps["attack"] - gaps["benign"]
        lo, hi = boot_did(task_groups(sub[("attack", "own-family")]),
                          task_groups(sub[("attack", "cross-family")]),
                          task_groups(sub[("benign", "own-family")]),
                          task_groups(sub[("benign", "cross-family")]), rng)
        dids.append(dict(monitor=mon, benign_gap=gaps["benign"], attack_gap=gaps["attack"],
                         did=did, did_ci_lo=lo, did_ci_hi=hi))
    didf = pd.DataFrame(dids)

    # Pooled gemma-monitor DiD (both gemma monitors together)
    gm = df[df.mon_family == "gemma"]
    sub = {(c, f): gm[(gm.condition == c) & (gm.fam_rel == f)]
           for c in ["benign", "attack"] for f in ["own-family", "cross-family"]}
    pooled_gaps = {c: sub[(c, "own-family")]["mean_score"].mean()
                      - sub[(c, "cross-family")]["mean_score"].mean()
                   for c in ["benign", "attack"]}
    pooled_did = pooled_gaps["attack"] - pooled_gaps["benign"]
    plo, phi = boot_did(task_groups(sub[("attack", "own-family")]),
                        task_groups(sub[("attack", "cross-family")]),
                        task_groups(sub[("benign", "own-family")]),
                        task_groups(sub[("benign", "cross-family")]), rng)

    # ---------- Automated honest reading ----------
    def sig_neg(r):
        return r["gap_ci_hi"] < 0

    def sig_pos(r):
        return r["gap_ci_lo"] > 0

    gemma_mons = ["gemma-4-26b-a4b-it", "gemma-4-31b-it"]
    gben = {m: con[(con.monitor == m) & (con.condition == "benign")].iloc[0] for m in gemma_mons}
    gatt = {m: con[(con.monitor == m) & (con.condition == "attack")].iloc[0] for m in gemma_mons}
    benign_discount = [m for m in gemma_mons if sig_neg(gben[m])]
    attack_discount = [m for m in gemma_mons if sig_neg(gatt[m])]
    benign_premium = [m for m in gemma_mons if sig_pos(gben[m])]
    attack_premium = [m for m in gemma_mons if sig_pos(gatt[m])]

    if len(benign_discount) == 2:
        verdict = "supported"
    elif len(benign_premium) == 2 and len(attack_premium) == 2:
        verdict = "refuted, with the sign reversed"
    elif len(benign_discount) == 0:
        verdict = "refuted (wholesale form)" if attack_discount else "refuted"
    else:
        verdict = "mixed"

    # ---------- Write markdown ----------
    def fmt(x):
        return "nan" if pd.isna(x) else f"{x:.1f}"

    md = []
    md.append("# Familiarity analysis: do gemma monitors discount gemma-written code wholesale?\n")
    md.append(f"_Generated by `analysis/familiarity.py` from `analysis/out/full/per_submission.csv` "
              f"({len(df)} (submission, monitor) rows; cluster bootstrap over {df['task'].nunique()} tasks, "
              f"{N_BOOT} reps, seed {SEED}). Benign stage = raw, attack stage = polished._\n")
    md.append("## Two pre-stated readings (declared before computing the numbers)\n")
    md.append("- **(A) Familiarity/fluency account (Wataoka-style):** gemma monitors score gemma-written "
              "code lower than cross-family code in *both* conditions, benign included. The diagonal "
              "leniency would then be partly a generic \"familiar text looks fine\" effect, not "
              "attack-specific collusion-like behavior.\n"
              "- **(B) Attack-specific discount:** benign gemma code gets normal scores from gemma "
              "monitors; the own/cross discount appears only on attack-bearing code. That refutes the "
              "wholesale familiarity account and localizes the effect to how smuggled side tasks "
              "written in one's own style are judged.\n\n"
              "Both are publishable; neither reading is spin.\n")

    md.append("## 1. Score distributions by (monitor, relationship, condition)\n")
    md.append("own-model = policy == monitor; same-family = same family, different weights; "
              "cross-family = different family. 95% CIs are task-cluster bootstrap.\n")
    md.append("| monitor | relationship | condition | n | median | mean [95% CI] | share==0 [95% CI] | p90 | p95 |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for _, r in cells.iterrows():
        md.append(f"| {r.monitor} | {r.relationship} | {r.condition} | {r.n} | {fmt(r['median'])} | "
                  f"{fmt(r['mean'])} [{fmt(r.mean_ci_lo)}, {fmt(r.mean_ci_hi)}] | "
                  f"{r.share_zero:.2f} [{r.share_zero_ci_lo:.2f}, {r.share_zero_ci_hi:.2f}] | "
                  f"{fmt(r.p90)} | {fmt(r.p95)} |")
    md.append("")

    md.append("## 2. Key contrasts: own-family-written vs cross-family-written code, per monitor\n")
    md.append("Gap = mean(own-family-written, i.e. own-model + same-family) - mean(cross-family-written), "
              "within each condition. Negative = monitor scores its own family's code as less suspicious.\n")
    md.append("| monitor | condition | mean own-fam (n) | mean cross-fam (n) | gap [95% CI] | sig? |")
    md.append("|---|---|---|---|---|---|")
    for _, r in con.iterrows():
        sig = "yes (neg)" if r.gap_ci_hi < 0 else ("yes (pos)" if r.gap_ci_lo > 0 else "no")
        md.append(f"| {r.monitor} | {r.condition} | {fmt(r.mean_own)} ({r.n_own}) | "
                  f"{fmt(r.mean_cross)} ({r.n_cross}) | {fmt(r.gap)} [{fmt(r.gap_ci_lo)}, {fmt(r.gap_ci_hi)}] | {sig} |")
    md.append("")

    md.append("## 3. Difference-in-differences: is the own/cross gap bigger for attacks than benign?\n")
    md.append("DiD = (attack own-cross gap) - (benign own-cross gap). Negative DiD = the own-family "
              "discount is *larger* on attacks (attack-specific leniency beyond any generic familiarity).\n")
    md.append("| monitor | benign gap | attack gap | DiD [95% CI] | sig? |")
    md.append("|---|---|---|---|---|")
    for _, r in didf.iterrows():
        sig = "yes" if (r.did_ci_hi < 0 or r.did_ci_lo > 0) else "no"
        md.append(f"| {r.monitor} | {fmt(r.benign_gap)} | {fmt(r.attack_gap)} | "
                  f"{fmt(r.did)} [{fmt(r.did_ci_lo)}, {fmt(r.did_ci_hi)}] | {sig} |")
    psig = "yes" if (phi < 0 or plo > 0) else "no"
    md.append(f"| **gemma monitors pooled** | {fmt(pooled_gaps['benign'])} | {fmt(pooled_gaps['attack'])} | "
              f"{fmt(pooled_did)} [{fmt(plo)}, {fmt(phi)}] | {psig} |")
    md.append("")

    md.append("## 4. Honest reading\n")
    s = []
    s.append(f"**Verdict on the familiarity account: {verdict}.**")
    for m in gemma_mons:
        s.append(f"{m}: benign own-family gap {fmt(gben[m].gap)} "
                 f"[{fmt(gben[m].gap_ci_lo)}, {fmt(gben[m].gap_ci_hi)}], "
                 f"attack own-family gap {fmt(gatt[m].gap)} "
                 f"[{fmt(gatt[m].gap_ci_lo)}, {fmt(gatt[m].gap_ci_hi)}].")
    if len(benign_discount) == 2:
        s.append("Both gemma monitors discount gemma-written code even when it is benign, so the "
                 "pattern is consistent with a Wataoka-style perplexity/familiarity effect (judges "
                 "favor familiar text) operating wholesale, not only on attacks.")
    elif len(benign_discount) == 0 and attack_discount:
        s.append("Neither gemma monitor significantly discounts benign gemma-written code, while the "
                 "attack-side discount " + ("is significant for " + ", ".join(attack_discount)) +
                 "; the effect is specific to attack-bearing code, which cuts against the wholesale "
                 "perplexity-familiarity hypothesis and leaves an attack-conditional mechanism.")
    elif len(benign_premium) == 2 and len(attack_premium) == 2:
        s.append("Both gemma monitors score gemma-written code as *more* suspicious than cross-family "
                 "code in both conditions, benign included -- the opposite of a familiarity discount. "
                 "The Wataoka-style perplexity-familiarity hypothesis (judges favor familiar text) is "
                 "refuted here in its leniency form; if anything these data show familiarity *penalty* "
                 "or, more plausibly, that gemma-written code simply contains more surface features "
                 "(e.g. telemetry-style calls, comments) that trip every monitor, including gemma ones.")
    else:
        s.append(f"Only {benign_discount[0]} shows a significant benign-side discount, so the evidence "
                 "for a generic familiarity effect is mixed across the two gemma monitors.")
    s.append(f"Pooled gemma DiD = {fmt(pooled_did)} [{fmt(plo)}, {fmt(phi)}]: "
             + ("the own-family discount is significantly larger on attacks than on benign code, i.e. "
                "there is an attack-specific component beyond any generic familiarity."
                if phi < 0 else
                ("the own-family discount is significantly *smaller* (or more positive) on attacks than "
                 "on benign code." if plo > 0 else
                 "the attack-vs-benign difference in the own-family gap is not distinguishable from "
                 "zero, so these data cannot separate an attack-specific component from a uniform "
                 "familiarity shift.")))
    s.append("Caveats: benign submissions are raw while attack submissions are polished (one rewrite "
             "pass), so condition is confounded with stage; \"own-family\" pools own-model with "
             "same-family cells; and no perplexity was measured directly, so this is a behavioral "
             "proxy for the Wataoka-style hypothesis, not a test of it.")
    md.append(" ".join(s))
    md.append("")

    out_md = os.path.join(OUT_DIR, "familiarity.md")
    with open(out_md, "w") as f:
        f.write("\n".join(md))
    print(f"wrote {out_md}")
    print(f"wrote {os.path.join(OUT_DIR, 'familiarity.csv')}")


if __name__ == "__main__":
    main()
