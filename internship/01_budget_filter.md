# 案1: 予算フィルター機能の追加

## ねらい
ユーザがランチ予算を指定できるようにし、よりニーズに合ったレコメンドを実現する。

## 短時間で改修可能な理由
- 既存のPOST `/roulette` APIは予算パラメータ（`budget`）を受け取る設計になっている。
- Hot Pepper APIの検索条件に予算を追加するだけで実装可能。
- UI側も予算入力欄を追加するだけで済む。
- 既存のビジネスロジックの一部修正で完結。

## 必要なビジネスロジック
- `src/lunch_roulette/services/restaurant_service.py`で、APIリクエスト時に予算条件をHot Pepper APIのパラメータに追加。
- 予算未指定時はデフォルト値（1200円）を利用。
- UI（`templates/index.html`）に予算入力欄を追加し、POST時に値を送信。
