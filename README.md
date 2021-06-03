# vapor-liquid-equilibrium-simulator

以下のような問題を考えるために作成しました。

>容積一定の容器を自由に動く壁で仕切り、左側にはジエチルエーテルをn[mol]、右側にはエタノールをn/2[mol]と窒素をn/2[mol]を入れる。
>この時、容器内の温度は100℃で圧力は800mmHgだった。この容器を0℃まで冷却したら、容器内の圧力はどのようになるか。

以下のようなgifが出力されます。
![gif](https://user-images.githubusercontent.com/56952494/120641242-55eed080-c4ae-11eb-910a-12df448d1935.gif)

## 使い方

### 1. ダウンロード
```bash
git clone https://github.com/hiro2620/vapor-liquid-equilibrium-simulator.git
cd vapor-liquid-equilibrium-simulator
```

### (1.1 必要なら仮想環境を作成)
```bash
python3 -m venv env
. ./env/bin/activate
```

### 2. 必要なライブラリのインストール
```bash
pip install -r requirements.txt
```

### 3. 実行
```bash
python3 main.py
```

## テスト環境
x86_64 Ubuntu 20.04.2 LTS

Python 3.8.5
