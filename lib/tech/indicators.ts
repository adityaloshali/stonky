import { RSI, MACD, SMA, BollingerBands } from 'technicalindicators';

export interface Candle { date: Date; open: number; high: number; low: number; close: number; volume?: number }

export function computeBasicSignals(candles: Candle[]) {
  const closes = candles.map(c => c.close);
  const rsi = RSI.calculate({ values: closes, period: 14 });
  const macd = MACD.calculate({ values: closes, fastPeriod: 12, slowPeriod: 26, signalPeriod: 9, SimpleMAOscillator: false, SimpleMASignal: false });
  const sma50 = SMA.calculate({ values: closes, period: 50 });
  const sma200 = SMA.calculate({ values: closes, period: 200 });
  const bb = BollingerBands.calculate({ period: 20, stdDev: 2, values: closes });
  return { rsi, macd, sma50, sma200, bb };
}

