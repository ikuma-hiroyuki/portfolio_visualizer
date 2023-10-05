from django import forms
from datetime import date

current_year = date.today().year


class BacktestSettingsForm(forms.Form):
    """
    バックテスト設定用のフォーム。
    """

    time_period = forms.ChoiceField(choices=((0, '年足'), (1, '月足'),), label="期間")

    choice_year = [(i, str(i)) for i in range(1985, current_year + 1)]
    start_year = forms.ChoiceField(choices=choice_year, label="開始年")
    end_year = forms.ChoiceField(choices=choice_year, initial=current_year, label="終了年")

    init_amount = forms.IntegerField(label="初期資金", initial=10000, min_value=0)


class PortfolioAssetForm(forms.Form):
    """
    ポートフォリオ設定用のフォーム。
    """
    pass
