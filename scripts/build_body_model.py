"""
Build the 3D fighter model used by components/body3d (fighter.glb).

Source: the MakeHuman base mesh (hm08), its default skeleton and skin weights, and the macro
targets for an athletic young male. All of these assets were released by the MakeHuman team
as CC0 (see https://github.com/makehumancommunity/makehuman, LICENSE.md, section C).

What the script does
  1. Shapes the neutral base mesh into an athletic male (race/gender, ideal proportions, muscle).
  2. Curls the fingers into a fist with linear-blend skinning, then folds finger, toe, face
     and breast bones into their parents so ~30 bones remain.
  3. Builds clothing shells from the skin itself (fight shorts, waistband, gloves, wrist
     straps, ankle bands) by pushing regions of the surface out along their normals. The shells
     share the skin weights, so they move with the body.
  4. Adds two morph targets, "heavy" and "lean", so the body follows weight-for-height.
  5. Writes a skinned glTF binary (metres, Y up, facing +Z).

Run:  python scripts/build_body_model.py      (downloads ~4 MB of assets on first run)
"""
from __future__ import annotations

import json
import struct
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".mh_cache"
OUT = ROOT / "components" / "body3d" / "fighter.glb"
RAW = "https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/"


def fetch(rel: str) -> Path:
    path = CACHE / rel
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        print("downloading", rel)
        urllib.request.urlretrieve(RAW + rel, path)
    return path


# ------------------------------------------------------------------ loading
def load_obj(path: Path):
    verts, faces, group = [], [], None
    for line in path.read_text().splitlines():
        if line.startswith("v "):
            verts.append([float(x) for x in line.split()[1:4]])
        elif line.startswith("g "):
            group = line.split()[1]
        elif line.startswith("f ") and group == "body":
            faces.append([int(tok.split("/")[0]) - 1 for tok in line.split()[1:]])
    return np.array(verts), faces


def load_target(path: Path, n: int) -> np.ndarray:
    d = np.zeros((n, 3))
    for line in path.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        i, x, y, z = line.split()
        d[int(i)] = (float(x), float(y), float(z))
    return d


MACRO = "targets/macrodetails/"
verts0, quads = load_obj(fetch("3dobjs/base.obj"))
N = len(verts0)
T = lambda name: load_target(fetch(MACRO + name + ".target"), N)

shape = (verts0
         + 0.5 * T("caucasian-male-young") + 0.5 * T("african-male-young")
         + 1.0 * T("proportions/male-young-averagemuscle-averageweight-idealproportions")
         + 1.0 * T("universal-male-young-maxmuscle-averageweight")
         # lean it out a little so the muscle shows, like a fighter on weigh-in day
         + 0.35 * (T("universal-male-young-maxmuscle-minweight") - T("universal-male-young-maxmuscle-averageweight")))
morphs = {
    "heavy": T("universal-male-young-maxmuscle-maxweight") - T("universal-male-young-maxmuscle-averageweight"),
    "lean": T("universal-male-young-maxmuscle-minweight") - T("universal-male-young-maxmuscle-averageweight"),
}

skel = json.loads(fetch("rigs/default.mhskel").read_text())
weights_raw = json.loads(fetch("rigs/default_weights.mhw").read_text())["weights"]
bones = skel["bones"]
joint_pos = {k: shape[v].mean(axis=0) for k, v in skel["joints"].items()}
head = {b: joint_pos[d["head"]] for b, d in bones.items()}
tail = {b: joint_pos[d["tail"]] for b, d in bones.items()}
parent = {b: d["parent"] for b, d in bones.items()}

# ------------------------------------------------------------------ per-vertex weights
vw: list[dict[str, float]] = [dict() for _ in range(N)]
for b, lst in weights_raw.items():
    for i, w in lst:
        vw[i][b] = vw[i].get(b, 0.0) + w


# ------------------------------------------------------------------ 2. curl the fingers into a fist
def rot(axis, ang):
    axis = axis / np.linalg.norm(axis)
    a, (x, y, z) = np.radians(ang), axis
    c, s, C = np.cos(a), np.sin(a), 1 - np.cos(a)
    return np.array([[c + x * x * C, x * y * C - z * s, x * z * C + y * s],
                     [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
                     [z * x * C - y * s, z * y * C + x * s, c + z * z * C]])


def affine(R, pivot):
    M = np.eye(4)
    M[:3, :3] = R
    M[:3, 3] = pivot - R @ pivot
    return M


pose = {}   # bone -> 4x4 world delta for the fist
for side in "LR":
    w_ = head[f"wrist.{side}"]
    mid, idx, pinky = head[f"finger3-1.{side}"], head[f"finger2-1.{side}"], head[f"finger5-1.{side}"]
    hand_dir = (mid - w_) / np.linalg.norm(mid - w_)
    across = (idx - pinky) / np.linalg.norm(idx - pinky)
    palm = np.cross(hand_dir, across)
    palm /= np.linalg.norm(palm)
    thumb = head[f"finger1-2.{side}"] - (w_ + mid) / 2
    if np.dot(thumb, palm) < 0:          # the thumb sits on the palm side
        palm = -palm
    for f, angles in [(1, (20, 30, 40)), (2, (68, 88, 62)), (3, (70, 90, 62)), (4, (72, 90, 62)),
                      (5, (74, 90, 62))]:
        M = np.eye(4)
        for k, ang in zip((1, 2, 3), angles):
            b = f"finger{f}-{k}.{side}"
            seg = tail[b] - head[b]
            axis_rest = np.cross(seg / np.linalg.norm(seg), palm)
            if f == 1:
                axis_rest = np.cross(seg / np.linalg.norm(seg), palm + 0.6 * across * (1 if side == "L" else 1))
            pivot = (M @ np.append(head[b], 1))[:3]
            axis = M[:3, :3] @ axis_rest
            M = affine(rot(axis, ang), pivot) @ M
            pose[b] = M

palm_n = {}
for side in "LR":
    w_ = head[f"wrist.{side}"]
    mid_, idx_, pinky_ = head[f"finger3-1.{side}"], head[f"finger2-1.{side}"], head[f"finger5-1.{side}"]
    hd_ = (mid_ - w_) / np.linalg.norm(mid_ - w_)
    ac_ = (idx_ - pinky_) / np.linalg.norm(idx_ - pinky_)
    pv = np.cross(hd_, ac_); pv /= np.linalg.norm(pv)
    if np.dot(head[f"finger1-2.{side}"] - (w_ + mid_) / 2, pv) < 0:
        pv = -pv
    palm_n[side] = pv.tolist()

posed = shape.copy()
for i, d in enumerate(vw):
    if not any(b in pose for b in d):
        continue
    tot = sum(d.values())
    acc = np.zeros(3)
    for b, w in d.items():
        p = (pose[b] @ np.append(shape[i], 1))[:3] if b in pose else shape[i]
        acc += w * p
    posed[i] = acc / tot

# ------------------------------------------------------------------ fold bones into ~30
KEEP = ["root", "spine05", "spine04", "spine03", "spine02", "spine01", "neck01", "neck02", "neck03",
        "head"]
for s in "LR":
    KEEP += [f"pelvis.{s}", f"upperleg01.{s}", f"upperleg02.{s}", f"lowerleg01.{s}",
             f"lowerleg02.{s}", f"foot.{s}", f"clavicle.{s}", f"shoulder01.{s}", f"upperarm01.{s}",
             f"upperarm02.{s}", f"lowerarm01.{s}", f"lowerarm02.{s}", f"wrist.{s}"]
KEEP = [b for b in KEEP if b in bones]


def kept(b):
    while b not in KEEP:
        b = parent[b]
    return b


order = []                              # parents before children
def visit(b):
    if b in order:
        return
    p = parent[b]
    if p is not None:
        visit(kept(p))
    order.append(b)
for b in KEEP:
    visit(b)
kparent = {b: (kept(parent[b]) if parent[b] else None) for b in order}
bidx = {b: i for i, b in enumerate(order)}

merged = []
for d in vw:
    m: dict[str, float] = {}
    for b, w in d.items():
        k = kept(b)
        m[k] = m.get(k, 0) + w
    top = sorted(m.items(), key=lambda kv: -kv[1])[:4]
    s = sum(w for _, w in top) or 1
    merged.append([(bidx[b], w / s) for b, w in top])
dominant = [max(m, key=lambda t: t[1])[0] if m else 0 for m in merged]

# ------------------------------------------------------------------ geometry
tris = []
for f in quads:
    tris.append((f[0], f[1], f[2]))
    if len(f) == 4:
        tris.append((f[0], f[2], f[3]))
tris = np.array(tris)
used = np.unique(tris)


def normals(P, tris):
    n = np.zeros_like(P)
    fn = np.cross(P[tris[:, 1]] - P[tris[:, 0]], P[tris[:, 2]] - P[tris[:, 0]])
    for k in range(3):
        np.add.at(n, tris[:, k], fn)
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    return n / np.where(ln == 0, 1, ln)


NRM = normals(posed, tris)
S = 0.1                                          # decimetres -> metres
B = {name: bidx[name] for name in order}


def region(pred):
    return np.array([i for i in used if pred(i)], dtype=int)


hipY = (head["upperleg01.L"][1] + head["upperleg01.R"][1]) / 2
kneeY = (head["lowerleg01.L"][1] + head["lowerleg01.R"][1]) / 2
hemY = hipY - 0.78 * (hipY - kneeY)              # compression shorts end just above the knee
waistY = head["spine04"][1]
crotchY = hipY - 0.35 * (hipY - kneeY)
short_bones = {B[b] for b in ["root", "spine05", "pelvis.L", "pelvis.R", "upperleg01.L", "upperleg01.R",
                              "upperleg02.L", "upperleg02.R", "spine04"] if b in B}

def crotch_front(i):
    x, y, _ = posed[i]
    near_mid = np.exp(-(x / 0.75) ** 2)                      # dm: within ~7 cm of the midline
    front = np.clip(NRM[i][2], 0, 1) ** 0.5
    band = np.clip((y - (crotchY - 0.9)) / 0.5, 0, 1) * np.clip((hipY + 0.3 - y) / 0.5, 0, 1)   # stays below the waistband
    return near_mid * front * band


shells = {}
shells["shorts"] = (region(lambda i: dominant[i] in short_bones and hemY <= posed[i][1] <= waistY),
                    lambda i: 0.03 + 0.11 * crotch_front(i))
                    # compression fit ~3 mm off the skin; the front of the crotch stands off up to ~1.4 cm
                    # so the fabric bridges smoothly between the thighs like real fight shorts
shells["waist"] = (region(lambda i: dominant[i] in short_bones and waistY - 0.4 <= posed[i][1] <= waistY + 0.05),
                   lambda i: 0.1)
# --- 4oz MMA gloves: padded knuckle shell, thin leather palm, open fingers, wide wrist strap
orig_dom = [max(d, key=d.get) if d else "" for d in vw]
adj = [set() for _ in range(N)]
for a_, b_, c_ in tris:
    adj[a_] |= {b_, c_}; adj[b_] |= {a_, c_}; adj[c_] |= {a_, b_}


def rings(vset):
    """Edge distance of every vertex in vset from the edge of vset (0 = on the boundary)."""
    inset = set(vset)
    dist = {v: 0 for v in vset if any(n not in inset for n in adj[v])}
    frontier = list(dist)
    while frontier:
        nxt = []
        for v in frontier:
            for n in adj[v]:
                if n in inset and n not in dist:
                    dist[n] = dist[v] + 1
                    nxt.append(n)
        frontier = nxt
    return dist


def smooth(vals, vset, it=4):
    inset = set(vset)
    for _ in range(it):
        vals = {v: 0.5 * vals[v] + 0.5 * np.mean([vals[n] for n in adj[v] if n in inset] or [vals[v]])
                for v in vset}
    return vals


glove_parts = {}          # name -> (vertex ids, offset dict, face filter)
for s in "LR":
    w_ = head[f"wrist.{s}"]
    knuckle = np.mean([head[f"finger{f}-1.{s}"] for f in (2, 3, 4, 5)], axis=0)
    f_dir = (knuckle - w_) / np.linalg.norm(knuckle - w_)
    pn = np.array(palm_n[s])
    dors = -pn
    kproj = float(np.dot(knuckle - w_, f_dir))
    proj = {i: float(np.dot(posed[i] - w_, f_dir)) for i in used}
    near = [i for i in used if dominant[i] in (B[f"lowerarm01.{s}"], B[f"lowerarm02.{s}"], B[f"wrist.{s}"])
            and np.linalg.norm(posed[i] - w_) < 1.6]
    STRAP_END = 0.22                                     # dm past the wrist joint where the strap stops
    STRAP_START = -0.75                                  # ~7.5 cm hook-and-loop cuff up the forearm
    covered, strap = [], []
    for i in near:
        o = orig_dom[i]                                  # e.g. "finger3-2.L": finger 3, segment 2
        if o.startswith("finger") and o[6] in "2345" and o[8] in "23":
            continue                                     # middle and tip of the fingers stay bare
        if o.startswith("finger1-3"):
            continue                                     # thumb tip bare
        if STRAP_START <= proj[i] <= STRAP_END + 0.06:
            strap.append(i)
        if proj[i] >= STRAP_END - 0.06 and (dominant[i] == B[f"wrist.{s}"] or proj[i] > 0.05):
            covered.append(i)
    # "how much does this point face the back of the hand / the knuckles", smoothed over the surface
    score = {}
    for i in covered:
        o, n = orig_dom[i], NRM[i]
        sc_ = np.dot(n, dors)
        if o.startswith("finger") and o[6] in "2345":
            sc_ = max(sc_, np.dot(n, f_dir) - 0.2)      # knuckle faces forward in a fist
        if o.startswith("finger1"):
            sc_ = -1.0                                   # thumb: leather
        score[i] = sc_
    score = smooth(score, covered, 6)
    pad = [i for i in covered if score[i] > -0.05]
    leather = list(covered)                              # leather under everything; pad sits on top
    padset = set(pad)
    pad = sorted(padset | {n for v in padset for n in adj[v] if n in set(covered)})   # overlap the seam
    rp, rl = rings(pad), rings(leather)
    thick = {}
    for i in pad:
        u = np.clip((proj[i] / kproj - 0.15) / 0.75, 0, 1)
        base = 0.14 + 0.19 * (u * u * (3 - 2 * u))      # ~1.4 cm by the wrist -> 3.3 cm over the knuckles
        if orig_dom[i].startswith("finger"):
            base = 0.31
        thick[i] = base * (0.5, 0.78, 0.92, 1.0)[min(rp[i], 3)]
    thick = smooth(thick, pad, 3)
    # finger tubes: a groove wherever the pad passes from one finger to the next
    fid = {i: orig_dom[i][6] for i in pad if orig_dom[i].startswith("finger") and orig_dom[i][6] in "2345"}
    groove = {i for i in fid if any(n in fid and fid[n] != fid[i] for n in adj[i])}
    near_g = {n for i in groove for n in adj[i] if n in fid} - groove
    for i in groove:
        thick[i] *= 0.42
    for i in near_g:
        thick[i] *= 0.8
    # stitched seam across the back of the hand, between the knuckle pad and the lower panel
    for i in pad:
        if i not in fid and 0.40 <= proj[i] / kproj <= 0.47:
            thick[i] *= 0.72
    lth = {i: 0.05 for i in leather}
    glove_parts[f"glove.{s}"] = (pad, thick, None, 2)
    glove_parts[f"glovePalm.{s}"] = (leather, lth, None, 0)
    rs = rings(strap)
    st_off = {i: 0.17 * (0.6 if rs[i] == 0 else 1.0) for i in strap}
    glove_parts[f"strap.{s}"] = (strap, st_off, None, 2)
    # label patch on the back of the strap (corner colour, gold on the dominant hand)
    across_ = np.cross(f_dir, pn)
    patch = [i for i in strap if np.dot(NRM[i], dors) > 0.35 and abs(np.dot(posed[i] - w_, across_)) < 0.33
             and -0.7 <= proj[i] <= 0.08 and rs[i] >= 1]
    glove_parts[f"strapPatch.{s}"] = (patch, {i: st_off[i] + 0.022 for i in patch}, None, 2)
    ank = head[f"foot.{s}"]
    shells[f"ankle.{s}"] = (region(lambda i, s=s, ank=ank: dominant[i] in (B[f"lowerleg02.{s}"], B[f"foot.{s}"])
                                   and ank[1] - 0.05 <= posed[i][1] <= ank[1] + 0.45),
                            lambda i: 0.09)


def submesh(vidx, offset=None, face_ok=None, relax=0):
    vidx = np.asarray(vidx, dtype=int)
    remap = -np.ones(N, dtype=int)
    remap[vidx] = np.arange(len(vidx))
    keep = np.all(remap[tris] >= 0, axis=1)
    if face_ok is not None:
        keep &= np.array([bool(k) and face_ok(t) for k, t in zip(keep, tris)])
    t = remap[tris[keep]]
    P = posed[vidx].copy()
    if offset is not None:
        off = np.array([offset[i] if isinstance(offset, dict) else offset(i) for i in vidx])
        P = P + NRM[vidx] * off[:, None]
    if relax:                                   # Laplacian smoothing: one padded block, not five fingers
        loc = {v: r for r, v in enumerate(vidx)}
        nb = [[loc[n] for n in adj[v] if n in loc] for v in vidx]
        edge = rings(list(vidx))
        for _ in range(relax):
            Q = P.copy()
            for r, ns in enumerate(nb):
                if ns and edge[vidx[r]] > 0:
                    Q[r] = 0.35 * P[r] + 0.65 * P[ns].mean(axis=0)
            P = Q
    J = np.zeros((len(vidx), 4), dtype=np.uint16)
    W = np.zeros((len(vidx), 4), dtype=np.float32)
    for r, i in enumerate(vidx):
        for c, (b, w) in enumerate(merged[i]):
            J[r, c], W[r, c] = b, w
    mt = {k: (v[vidx] * S).astype(np.float32) for k, v in morphs.items()}
    return dict(P=(P * S).astype(np.float32), N=normals(P, t).astype(np.float32), J=J, W=W,
                I=t.astype(np.uint32).ravel(), morph=mt)


meshes = {"body": submesh(used)}
for name, (vidx, off) in shells.items():
    meshes[name] = submesh(vidx, off)
    print(f"{name:12s} {len(vidx):6d} verts")
for name, (vidx, off, ok, rl) in glove_parts.items():
    meshes[name] = submesh(vidx, off, ok, rl)
    print(f"{name:12s} {len(vidx):6d} verts, {len(meshes[name]['I']) // 3} faces")

# ------------------------------------------------------------------ bone frames
def frame(b):
    y = tail[b] - head[b]
    y = y / np.linalg.norm(y)
    ref = np.array([1.0, 0, 0]) if abs(y[0]) < 0.9 else np.array([0, 0, 1.0])
    x = ref - y * np.dot(ref, y)
    x /= np.linalg.norm(x)
    z = np.cross(x, y)
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = x, y, z, head[b] * S
    return M


def mat_to_quat(R):
    t = np.trace(R)
    if t > 0:
        s = np.sqrt(t + 1.0) * 2
        return [(R[2, 1] - R[1, 2]) / s, (R[0, 2] - R[2, 0]) / s, (R[1, 0] - R[0, 1]) / s, 0.25 * s]
    i = int(np.argmax(np.diag(R)))
    j, k = (i + 1) % 3, (i + 2) % 3
    s = np.sqrt(1.0 + R[i, i] - R[j, j] - R[k, k]) * 2
    q = [0.0, 0.0, 0.0, 0.0]
    q[i] = 0.25 * s
    q[j] = (R[j, i] + R[i, j]) / s
    q[k] = (R[k, i] + R[i, k]) / s
    q[3] = (R[k, j] - R[j, k]) / s
    return q


world = {b: frame(b) for b in order}
eye = {s: (joint_pos[f"eye.{s}____head"] * S).tolist() for s in "LR"}
palm_dir = {}
for s in "LR":
    w_ = head[f"wrist.{s}"]
    mid, idx, pinky = head[f"finger3-1.{s}"], head[f"finger2-1.{s}"], head[f"finger5-1.{s}"]
    hd = (mid - w_) / np.linalg.norm(mid - w_)
    ac = (idx - pinky) / np.linalg.norm(idx - pinky)
    pn = np.cross(hd, ac); pn /= np.linalg.norm(pn)
    if np.dot(head[f"finger1-2.{s}"] - (w_ + mid) / 2, pn) < 0:
        pn = -pn
    palm_dir[s] = pn.tolist()

# how far the gloved fist reaches past the wrist joint, along the hand (metres)
fist_len = {}
for s_ in "LR":
    w_ = head[f"wrist.{s_}"]
    d_ = tail[f"wrist.{s_}"] - w_
    d_ /= np.linalg.norm(d_)
    g_ = meshes[f"glove.{s_}"]["P"] / S
    fist_len[s_] = float(((g_ - w_) @ d_).max() * S)

# ------------------------------------------------------------------ write GLB
blob = bytearray()
views, accessors = [], []


def add(arr: np.ndarray, kind: str, comp: int, target=None, minmax=False):
    data = np.ascontiguousarray(arr).tobytes()
    while len(blob) % 4:
        blob.append(0)
    view = {"buffer": 0, "byteOffset": len(blob), "byteLength": len(data)}
    if target:
        view["target"] = target
    blob.extend(data)
    views.append(view)
    acc = {"bufferView": len(views) - 1, "componentType": comp, "type": kind,
           "count": int(arr.shape[0] if kind != "SCALAR" else arr.size)}
    if minmax:
        acc["min"] = arr.min(axis=0).tolist()
        acc["max"] = arr.max(axis=0).tolist()
    accessors.append(acc)
    return len(accessors) - 1


FLOAT, U16, U32 = 5126, 5123, 5125
nodes, gl_meshes, materials = [], [], []
for b in order:
    p = kparent[b]
    local = np.linalg.inv(world[p]) @ world[b] if p else world[b]
    node = {"name": b, "translation": local[:3, 3].tolist(), "rotation": mat_to_quat(local[:3, :3])}
    if b.startswith("wrist."):
        node["extras"] = {"palm": palm_dir[b[-1]]}
    nodes.append(node)
for b in order:
    kids = [bidx[c] for c in order if kparent[c] == b]
    if kids:
        nodes[bidx[b]]["children"] = kids

ibm = np.stack([np.linalg.inv(world[b]).T for b in order]).astype(np.float32)   # column-major
skin = {"joints": list(range(len(order))), "skeleton": 0,
        "inverseBindMatrices": add(ibm.reshape(-1, 16), "MAT4", FLOAT)}

for name, m in meshes.items():
    materials.append({"name": name, "pbrMetallicRoughness": {"baseColorFactor": [.4, .4, .4, 1]},
                      "doubleSided": name != "body"})
    prim = {"attributes": {"POSITION": add(m["P"], "VEC3", FLOAT, 34962, True),
                           "NORMAL": add(m["N"], "VEC3", FLOAT, 34962),
                           "JOINTS_0": add(m["J"], "VEC4", U16, 34962),
                           "WEIGHTS_0": add(m["W"], "VEC4", FLOAT, 34962)},
            "indices": add(m["I"], "SCALAR", U32, 34963),
            "material": len(materials) - 1,
            "targets": [{"POSITION": add(m["morph"][k], "VEC3", FLOAT, 34962, True)} for k in morphs]}
    gl_meshes.append({"name": name, "primitives": [prim], "weights": [0.0] * len(morphs),
                      "extras": {"targetNames": list(morphs)}})
    nodes.append({"name": name, "mesh": len(gl_meshes) - 1, "skin": 0})

gltf = {
    "asset": {"version": "2.0", "generator": "build_body_model.py",
              "copyright": "Body mesh, skeleton, weights and targets: MakeHuman (CC0)."},
    "scene": 0,
    "scenes": [{"nodes": [0] + list(range(len(order), len(nodes)))}],
    "nodes": nodes, "meshes": gl_meshes, "materials": materials, "skins": [skin],
    "accessors": accessors, "bufferViews": views, "buffers": [{"byteLength": len(blob)}],
    "extras": {"eyes": eye, "height": float((posed[used][:, 1].max() - posed[used][:, 1].min()) * S),
               "floor": float(posed[used][:, 1].min() * S), "top": float(posed[used][:, 1].max() * S),
               "fist": fist_len},
}
js = json.dumps(gltf, separators=(",", ":")).encode()
js += b" " * ((4 - len(js) % 4) % 4)
while len(blob) % 4:
    blob.append(0)
glb = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(blob))
glb += struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(blob), 0x004E4942) + bytes(blob)
OUT.write_bytes(glb)
print(f"wrote {OUT.relative_to(ROOT)}  {len(glb) / 1e6:.2f} MB, {len(order)} bones, {len(used)} body verts")
