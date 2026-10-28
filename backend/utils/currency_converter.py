"""
Currency Converter - USD to KSH conversion
"""

class CurrencyConverter:
    """Convert currencies with real-time rates"""
    
    # Exchange rate (update periodically from API in production)
    # 1 USD = 129.50 KSH (as of Jan 2026)
    RATES = {
        'USD_TO_KSH': 129.50,
        'KSH_TO_USD': 1 / 129.50
    }
    
    @staticmethod
    def usd_to_ksh(usd_amount):
        """Convert USD to KSH"""
        if usd_amount is None or usd_amount == 0:
            return 0.0
        return round(usd_amount * CurrencyConverter.RATES['USD_TO_KSH'], 2)
    
    @staticmethod
    def ksh_to_usd(ksh_amount):
        """Convert KSH to USD"""
        if ksh_amount is None or ksh_amount == 0:
            return 0.0
        return round(ksh_amount * CurrencyConverter.RATES['KSH_TO_USD'], 2)
    
    @staticmethod
    def get_rate():
        """Get current USD to KSH rate"""
        return CurrencyConverter.RATES['USD_TO_KSH']
    
    @staticmethod
    def update_rate(new_rate):
        """Update exchange rate (for production API integration)"""
        CurrencyConverter.RATES['USD_TO_KSH'] = new_rate
        CurrencyConverter.RATES['KSH_TO_USD'] = 1 / new_rate


# Global instance
currency_converter = CurrencyConverter()
