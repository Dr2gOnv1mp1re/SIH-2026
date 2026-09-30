# Quantum Risk AI — Mathematical Investment Optimization
## Mixed-Integer Linear Programming (MILP), 0-1 Knapsack & Prerequisite DAG Constraints

### 1. The Capital Allocation Dilemma in Cybersecurity
A typical enterprise CISO faces a complex portfolio optimization challenge:
- Available budget is finite (e.g. ₹1.00 Crore).
- Multiple security vendors propose diverse solutions (e.g. automated patching, privileged access management, micro-segmentation, EDR, immutable backup).
- Controls exhibit **interdependencies** (e.g. Micro-segmentation requires prior Network Inventory).
- Security investments face **diminishing marginal returns** (spending more money does not linearly eliminate all risk).

Naive heuristics (such as greedy ranking by cost or alphabetical selection) produce suboptimal allocations. Quantum Risk AI formulates and solves this problem using **Google OR-Tools SCIP Mixed-Integer Linear Programming (MILP)**.

---

### 2. Mathematical Formulation

#### 2.1 Decision Variables
Let $N$ be the set of candidate security controls ($N = 20$). For each control $i \in N$:
$$x_i \in \{0, 1\} \quad \text{where } x_i = 1 \text{ if control } i \text{ is selected, } 0 \text{ otherwise.}$$

#### 2.2 Objective Function
Maximize total modeled financial risk reduction:
$$\max \sum_{i=1}^{N} R_i \cdot x_i$$
Where $R_i$ is the modeled annual risk reduction in Rupees (₹) attributed to control $i$.

#### 2.3 Primary Budget Constraint
The total cost of implementation cannot exceed the CISO's allocated capital budget $B$:
$$\sum_{i=1}^{N} C_i \cdot x_i \le B$$
Where $C_i$ is the total annual cost of implementation for control $i$.

#### 2.4 Prerequisite Control DAG Constraints
Certain security controls cannot function without foundational controls being in place. For any dependency pair $(j, k)$ where control $j$ depends on prerequisite control $k$:
$$x_j \le x_k$$
*(Control $j$ can only be activated if control $k$ is also selected).*

#### 2.5 Mutually Exclusive / Alternative Control Constraints
If two controls represent alternative implementations of the same capability:
$$x_a + x_b \le 1$$

---

### 3. Solved Optimization Portfolio for ABC Bank

Under a standard Board-authorized budget of **₹1.00 Crore (₹10,000,000)**:

| Control Code | Control Name | Implementation Cost | Modeled Risk Reduction | Efficiency Ratio (ROI) |
|:---|:---|:---:|:---:|:---:|
| `CTRL-PATCH` | Automated Critical Patching | ₹18,00,000 | ₹75,00,000 | **4.17x** |
| `CTRL-MFA` | Privileged Identity MFA | ₹12,00,000 | ₹45,00,000 | **3.75x** |
| `CTRL-EDR` | Next-Gen EDR / XDR | ₹25,00,000 | ₹80,00,000 | **3.20x** |
| `CTRL-SEG` | Network Micro-segmentation | ₹20,00,000 | ₹60,00,000 | **3.00x** |
| `CTRL-BACKUP`| Air-Gapped WORM Backup | ₹10,00,000 | ₹35,00,000 | **3.50x** |
| **OPTIMAL PORTFOLIO** | **5 Selected Controls** | **₹85,00,000** | **₹2,60,00,000** | **3.06x** |

#### Key Fiduciary Takeaways:
1. **Total Invested:** ₹85.0 Lakh (leaves ₹15.0 Lakh as a 15% regulatory contingency reserve).
2. **Total Modeled Risk Reduction:** ₹2.60 Crore (Expected Annual Loss drops from ₹4.60 Cr to ₹2.00 Cr).
3. **Efficiency Metric:** **3.06x ROI** (Every ₹1 invested yields ₹3.06 in risk reduction).
4. **Subsequent Controls:** Remaining candidate controls have marginal ROI $< 1.2\text{x}$, validating the mathematical decision to reserve the remaining ₹15 Lakh.
