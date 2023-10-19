from datetime import date, datetime

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import yfinance as yf
from dateutil.relativedelta import relativedelta


def _get_youngest_ipo_date(tickers: list) -> date:
    """
    複数銘柄のうちで市場公開日が最も若い銘柄の次の月の1日を返す

    一番若い日付に合わせないと歯抜けになるため

    :param tickers: 銘柄リスト
    :return: 最も若い銘柄の次の月の1日
    """

    trading_start_days = []
    for ticker in yf.Tickers(tickers).tickers.values():
        asset_first_date = datetime.utcfromtimestamp(ticker.history_metadata["firstTradeDate"]).date()
        next_month = (asset_first_date + relativedelta(months=1)).replace(day=1)
        trading_start_days.append(next_month)
    return max(trading_start_days)


def _fetch_closing_prices(tickers: dict[str:float], start_date: date, end_date: date, interval: str = "1mo"):
    """
    銘柄の終値を取得

    :param tickers: 銘柄
    :param start_date: 取得開始日
    :param end_date: 取得終了日
    :param interval: 取得間隔
    :return:pandas.DataFrame 調整後の終値
    """

    asset_data_frame = yf.download(list(tickers.keys()), start=start_date, end=end_date, interval=interval)["Adj Close"]
    return asset_data_frame


def _calculate_asset_units(ticker_data, initial_amount, prices):
    """
    初期投資額と各銘柄の割合から、銘柄ごとの購入可能単位数を計算する

    :param ticker_data: {銘柄名: {"ratio": 割合}} 形式の辞書
    :param initial_amount: 初期投資額
    :param prices: 銘柄の終値データ。Pandas DataFrame オブジェクト
    :return: {"ratio": 割合, "unit": 単位数} 形式に更新された ticker_data
    """

    for ticker, data in ticker_data.items():
        ratio = data["ratio"]
        price = prices[ticker].iloc[0]
        data["unit"] = int((initial_amount * ratio) / 100 / price)

    return ticker_data


def _calculate_asset_amount(ticker_data, prices):
    """
    銘柄ごとの購入可能単位数と各銘柄の終値データから、各銘柄の資産額を計算する

    :param ticker_data: {銘柄名: {"ratio": 割合, "unit": 単位数}} 形式の辞書
    :param prices: 銘柄の終値データ。Pandas DataFrame オブジェクト
    :return: Pandas DataFrame オブジェクト (各銘柄の終値に対して、各銘柄の単位数を乗算したもの)
    """

    tickers_amount = prices.copy()
    for ticker, data in ticker_data.items():
        tickers_amount[ticker] = tickers_amount[ticker] * data["unit"]

    tickers_amount["Total"] = tickers_amount.sum(axis=1)

    return tickers_amount


def _plot_chart(asset):
    """
    資産額のチャートを描画する

    param asset: 資産額のデータ。Pandas DataFrame オブジェクト
    param ticker_names: 銘柄名のリスト
    """

    ticker_names = asset.columns.tolist()
    for ticker in ticker_names:
        plt.plot(asset[ticker], label=ticker)

    plt.title("Closing Prices")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()

    plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: format(int(x), ',')))

    plt.show()


def fetch_asset_amount(initial_amount: int, tickers: dict[str, dict[str, float]]):
    """
    初期投資額と銘柄の割合から、各銘柄の資産額を計算する
    :param initial_amount: 初期投資額
    :param tickers: 銘柄
    """

    trimmed_ticker = {ticker: data for ticker, data in tickers.items() if ticker}
    youngest_ipo_date = _get_youngest_ipo_date(list(trimmed_ticker.keys()))
    closing_prices = _fetch_closing_prices(tickers=trimmed_ticker, start_date=youngest_ipo_date, end_date=date.today())
    asset_units = _calculate_asset_units(trimmed_ticker, initial_amount, closing_prices)
    asset_amount = _calculate_asset_amount(asset_units, closing_prices)
    return asset_amount


if __name__ == "__main__":
    ticker_dict = {
        "SPY": {"ratio": 60.0, "unit": None},
        "TLT": {"ratio": 40.0, "unit": None},
        "": {"ratio": 0.0, "unit": None}  # 不正データテスト用
    }
    amount = fetch_asset_amount(10_000, ticker_dict)
    _plot_chart(amount)

    print(ticker_dict)
    print(amount.tail())
