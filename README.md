# Pricing-Options


A hands-on playground for **option pricing and Greeks**.

The goal is to show and compare the main numerical methods used in practice:
analytic closed-form formulas, trees, Monte Carlo, and finite-difference PDEs.

---

## Features

- **Instruments & market data**
- European / American options, payoffs, market environment (rates, dividends, vol).

- **Models**
- Black–Scholes, Bachelier, and stubs for more advanced models (Heston, Local Vol).

- **Pricing methods**
- Analytic closed-form formulas (BS, Bachelier, digital)
- Binomial & trinomial trees (European & American)
- Monte Carlo (vanilla, variance reduction, Longstaff–Schwartz for American)
- Finite-difference PDE (Crank–Nicolson for Black–Scholes)

- **Greeks & risk**
- Analytic Greeks under Black–Scholes
- Numerical Greeks (bump-and-revalue, pathwise in MC)

- **Implied volatility & smile**
- Implied vol inversion
- Simple smile / surface construction from option chains

- **Educational notebooks**
- Each method is illustrated with a dedicated notebook and explanatory plots.

---

## Repository structure

See [`docs/methods_overview.md`](docs/methods_overview.md) for a high-level explanation of each pricing method and when to use it.

```text
option_pricing_lab/ # Python package
notebooks/ # Jupyter notebooks (experiments)
examples/ # Small runnable scripts
data/ # Sample option chains / market data
tests/ # Pytest unit tests
docs/ # Additional documentation
