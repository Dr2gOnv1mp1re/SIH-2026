"""
Monte Carlo Simulation Engine for Cyber Risk Quantification.
Performs stochastic sampling under uncertainty (default 10,000 iterations):
- Loss Event Frequency: Poisson process (parameter lambda = LEF) or Bernoulli trial
- Loss Magnitude (Severity): Lognormal distribution centered at Single Loss Expectancy (SLE)
Returns Mean, Median (P50), P10, P25, P50, P75, P90, P95, Minimum, Maximum, and distribution histogram bins.
"""

import math
import random
from typing import Dict, List, Any, Optional

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

def run_monte_carlo_simulation(
    base_loss: float,
    base_probability: Optional[float] = None,
    loss_event_frequency: Optional[float] = None,
    num_iterations: int = 10000,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Simulates stochastic cyber incident loss distributions over thousands of iterations.
    Parameters represent uncertainty in the model inputs:
    - base_loss: Single Loss Expectancy (SLE in INR)
    - loss_event_frequency: Annualized Rate of Occurrence (ARO / LEF in incidents / year)
    - base_probability: Probability of occurrence in 1 year (P = 1 - exp(-LEF))
    Percentiles represent the Annualized Loss Exposure distribution under uncertainty.
    """
    num_iterations = max(100, min(50000, num_iterations))

    # Resolve frequency parameter (lambda)
    if loss_event_frequency is not None:
        lam = max(0.01, min(10.0, float(loss_event_frequency)))
        prob = round(1.0 - math.exp(-lam), 4)
    elif base_probability is not None:
        prob = max(0.001, min(0.999, float(base_probability)))
        lam = -math.log(1.0 - prob)
    else:
        lam = 0.50
        prob = round(1.0 - math.exp(-lam), 4)

    sigma = 0.50  # Lognormal shape parameter representing financial severity uncertainty
    mu = math.log(max(1000.0, base_loss)) - (sigma ** 2) / 2.0

    if HAS_NUMPY:
        rng = np.random.default_rng(seed)

        # Sample number of annual loss events from Poisson distribution
        # If lam is small, this behaves like Bernoulli(p); for multiple events, models compound loss
        num_events = rng.poisson(lam, num_iterations)
        annual_outcomes = np.zeros(num_iterations, dtype=np.float64)

        for i in range(num_iterations):
            k = int(num_events[i])
            if k > 0:
                # Sum of k independent loss occurrences
                event_losses = rng.lognormal(mu, sigma, k)
                annual_outcomes[i] = float(np.sum(event_losses))
            else:
                annual_outcomes[i] = 0.0

        p5 = float(np.percentile(annual_outcomes, 5))
        p10 = float(np.percentile(annual_outcomes, 10))
        p25 = float(np.percentile(annual_outcomes, 25))
        p50 = float(np.percentile(annual_outcomes, 50))
        p75 = float(np.percentile(annual_outcomes, 75))
        p90 = float(np.percentile(annual_outcomes, 90))
        p95 = float(np.percentile(annual_outcomes, 95))
        mean_val = float(np.mean(annual_outcomes))
        min_val = float(np.min(annual_outcomes))
        max_val = float(np.max(annual_outcomes))

        # Histogram (20 bins)
        counts, bin_edges = np.histogram(annual_outcomes, bins=20)
        histogram = [
            {
                "bin_start": round(float(bin_edges[i]), 2),
                "bin_end": round(float(bin_edges[i+1]), 2),
                "count": int(counts[i]),
                "label": f"₹{round(bin_edges[i]/100000, 1)}L - ₹{round(bin_edges[i+1]/100000, 1)}L"
            }
            for i in range(len(counts))
        ]
    else:
        random.seed(seed)
        annual_outcomes = []
        for _ in range(num_iterations):
            # Poisson approximation using Knuth's algorithm
            L = math.exp(-lam)
            k = 0
            p_val = 1.0
            while True:
                k += 1
                p_val *= random.random()
                if p_val <= L:
                    break
            k -= 1

            iter_loss = 0.0
            for _ in range(k):
                u1, u2 = random.random(), random.random()
                z = math.sqrt(-2 * math.log(max(1e-9, u1))) * math.cos(2 * math.pi * u2)
                loss_val = math.exp(mu + sigma * z)
                iter_loss += loss_val
            annual_outcomes.append(iter_loss)

        annual_outcomes.sort()
        p5 = annual_outcomes[int(num_iterations * 0.05)]
        p10 = annual_outcomes[int(num_iterations * 0.10)]
        p25 = annual_outcomes[int(num_iterations * 0.25)]
        p50 = annual_outcomes[int(num_iterations * 0.50)]
        p75 = annual_outcomes[int(num_iterations * 0.75)]
        p90 = annual_outcomes[int(num_iterations * 0.90)]
        p95 = annual_outcomes[int(num_iterations * 0.95)]
        mean_val = sum(annual_outcomes) / len(annual_outcomes)
        min_val = min(annual_outcomes)
        max_val = max(annual_outcomes)

        step = (max_val - min_val) / 20.0
        histogram = []
        for i in range(20):
            b_start = min_val + i * step
            b_end = b_start + step
            c = sum(1 for v in annual_outcomes if b_start <= v < b_end or (i == 19 and v == max_val))
            histogram.append({
                "bin_start": round(b_start, 2),
                "bin_end": round(b_end, 2),
                "count": c,
                "label": f"₹{round(b_start/100000, 1)}L - ₹{round(b_end/100000, 1)}L"
            })

    return {
        "num_iterations": num_iterations,
        "modeled_label": "MODELED SIMULATION",
        "mean_expected_loss": round(mean_val, 2),
        "mean": round(mean_val, 2),
        "mean_loss": round(mean_val, 2),
        "median": round(p50, 2),
        "median_loss": round(p50, 2),
        "minimum_loss": round(min_val, 2),
        "maximum_loss": round(max_val, 2),
        "min_loss": round(min_val, 2),
        "max_loss": round(max_val, 2),
        "percentiles": {
            "p5": round(p5, 2),
            "p10": round(p10, 2),
            "p25": round(p25, 2),
            "p50": round(p50, 2),
            "p50_median": round(p50, 2),
            "p75": round(p75, 2),
            "p90": round(p90, 2),
            "p95": round(p95, 2)
        },
        "histogram": histogram,
        "distribution_parameters": {
            "loss_distribution": f"Lognormal (mu={round(mu, 3)}, sigma={sigma})",
            "frequency_distribution": f"Poisson (lambda={round(lam, 3)} incidents/year)",
            "annual_probability": prob,
            "base_single_loss_expectancy": base_loss
        },
        "units": {
            "losses": "INR (₹) / year",
            "frequency": "incidents / year"
        },
        "disclaimer": "Monte Carlo simulated outcomes reflect parameter uncertainty. Not guaranteed balance-sheet losses."
    }

