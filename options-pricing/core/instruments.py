"""
Core financial instruments used in the option pricing library.

This module defines:
- Underlying: the asset on which options are written
- OptionType: call / put
- OptionStyle: European / American / Bermudan (placeholder)
- BaseOption: common fields for all options
- EuropeanOption / AmericanOption: concrete vanilla options

The actual payoff functions (call, put, digital, etc.) are implemented
in `payoff.py` to keep a clean separation between product definition
and payoff evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


# --------------------------------------------------------------------------- #
# Enumerations
# --------------------------------------------------------------------------- #

class OptionType(str, Enum):
    """Type of vanilla option: call or put."""

    CALL = "call"
    PUT = "put"

    @classmethod
    def from_str(cls, value: str) -> "OptionType":
        """Case-insensitive constructor from a string."""
        value = value.lower().strip()
        if value in {"c", "call"}:
            return cls.CALL
        if value in {"p", "put"}:
            return cls.PUT
        raise ValueError(f"Unknown option type: {value!r}")


class OptionStyle(str, Enum):
    """Exercise style of the option."""

    EUROPEAN = "european"
    AMERICAN = "american"
    BERMUDAN = "bermudan"  # placeholder for more complex products

    @classmethod
    def from_str(cls, value: str) -> "OptionStyle":
        value = value.lower().strip()
        if value in {"e", "euro", "european"}:
            return cls.EUROPEAN
        if value in {"a", "amer", "american"}:
            return cls.AMERICAN
        if value in {"b", "bermudan"}:
            return cls.BERMUDAN
        raise ValueError(f"Unknown option style: {value!r}")


# --------------------------------------------------------------------------- #
# Underlying asset
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Underlying:
    """
    Underlying asset on which an option is written.

    Parameters
    ----------
    symbol : str
        Ticker or identifier of the asset (e.g. "AAPL", "SPX", "EURUSD").
    spot : float
        Current spot price of the underlying.
    currency : str, optional
        Quotation currency (e.g. "EUR", "USD"). Default is "EUR".
    asset_type : str, optional
        Type of asset (e.g. "equity", "fx", "index", "rate"). Informational.
    """

    symbol: str
    spot: float
    currency: str = "EUR"
    asset_type: str = "equity"

    def __post_init__(self) -> None:
        if self.spot <= 0:
            raise ValueError("Underlying spot must be strictly positive.")


# --------------------------------------------------------------------------- #
# Base option class
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class BaseOption:
    """
    Base class for vanilla options.

    This class is not meant to be used directly; prefer `EuropeanOption`
    or `AmericanOption`.

    Parameters
    ----------
    underlying : Underlying
        Underlying asset.
    strike : float
        Option strike.
    maturity : date
        Calendar date of option maturity.
    option_type : OptionType
        Call or put.
    style : OptionStyle
        Exercise style (European, American, Bermudan).
    notional : float, optional
        Notional amount. Default: 1.0 (per-unit option).
    """

    underlying: Underlying
    strike: float
    maturity: date
    option_type: OptionType
    style: OptionStyle
    notional: float = 1.0

    def __post_init__(self) -> None:
        if self.strike <= 0:
            raise ValueError("Strike must be strictly positive.")
        if self.maturity is None:
            raise ValueError("Maturity date must be provided.")
        if self.notional <= 0:
            raise ValueError("Notional must be strictly positive.")

    # -------- Convenience properties -------- #

    @property
    def is_call(self) -> bool:
        return self.option_type == OptionType.CALL

    @property
    def is_put(self) -> bool:
        return self.option_type == OptionType.PUT

    @property
    def symbol(self) -> str:
        """Shortcut to the underlying symbol."""
        return self.underlying.symbol

    # -------- Time to maturity utilities -------- #

    def time_to_maturity(
        self,
        valuation_date: date,
        day_count: str = "ACT/365",
    ) -> float:
        """
        Compute the year fraction between valuation date and maturity.

        Parameters
        ----------
        valuation_date : date
            Date at which we value the option.
        day_count : str, optional
            Day count convention ("ACT/365", "ACT/360", "30/360").

        Returns
        -------
        float
            Time to maturity in years (can be negative if valuation_date > maturity).
        """
        if not isinstance(valuation_date, date):
            raise TypeError("valuation_date must be a datetime.date instance.")
        return year_fraction(valuation_date, self.maturity, day_count=day_count)


# --------------------------------------------------------------------------- #
# Concrete vanilla options
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class EuropeanOption(BaseOption):
    """Vanilla European option. Exercise only allowed at maturity."""

    def __init__(
        self,
        underlying: Underlying,
        strike: float,
        maturity: date,
        option_type: OptionType | str,
        notional: float = 1.0,
    ) -> None:

        if isinstance(option_type, str):
            option_type = OptionType.from_str(option_type)

        object.__setattr__(self, "underlying", underlying)
        object.__setattr__(self, "strike", strike)
        object.__setattr__(self, "maturity", maturity)
        object.__setattr__(self, "option_type", option_type)
        object.__setattr__(self, "style", OptionStyle.EUROPEAN)
        object.__setattr__(self, "notional", notional)

        self.__post_init__()


@dataclass(frozen=True)
class AmericanOption(BaseOption):
    """Vanilla American option. Exercise allowed any time before maturity."""

    def __init__(
        self,
        underlying: Underlying,
        strike: float,
        maturity: date,
        option_type: OptionType | str,
        notional: float = 1.0,
    ) -> None:

        if isinstance(option_type, str):
            option_type = OptionType.from_str(option_type)

        object.__setattr__(self, "underlying", underlying)
        object.__setattr__(self, "strike", strike)
        object.__setattr__(self, "maturity", maturity)
        object.__setattr__(self, "option_type", option_type)
        object.__setattr__(self, "style", OptionStyle.AMERICAN)
        object.__setattr__(self, "notional", notional)

        self.__post_init__()


# --------------------------------------------------------------------------- #
# Helper: year fraction
# --------------------------------------------------------------------------- #

def year_fraction(
    start: date,
    end: date,
    day_count: str = "ACT/365",
) -> float:
    """
    Compute year fraction according to a simple day-count convention.

    Parameters
    ----------
    start : date
        Start date.
    end : date
        End date.
    day_count : str, optional
        Day count convention: "ACT/365", "ACT/360", "30/360".

    Returns
    -------
    float
        Year fraction (can be negative if end < start).
    """
    if not isinstance(start, date) or not isinstance(end, date):
        raise TypeError("start and end must be datetime.date instances.")

    dc = day_count.upper()

    if dc == "ACT/365":
        return (end - start).days / 365.0

    elif dc == "ACT/360":
        return (end - start).days / 360.0

    elif dc == "30/360":
        # Simple 30/360 US approximation
        d1 = min(start.day, 30)
        d2 = min(end.day, 30)
        days = (
            (end.year - start.year) * 360
            + (end.month - start.month) * 30
            + (d2 - d1)
        )
        return days / 360.0

    else:
        raise ValueError(f"Unsupported day count convention: {day_count!r}")
