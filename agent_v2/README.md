# ConnectX 智能体 v2

分析报告和改动说明见 [REPORT.md](REPORT.md)。

## 可直接提交的文件

- `submission/submission_v2.tar.gz`：新版本（推荐）。根目录包含 `main.py`、`cx_solver_v1.so`、`cx_solver_v2.so`、`cx_book.bin`、`cx_traps.bin`。
- `submission/submission_v1.tar.gz`：旧版本，留作回退。

提交（自己操作）：网页上点 "Submit Agent" 上传，或者：

```bash
kaggle competitions submit -c connectx -f agent_v2/submission/submission_v2.tar.gz -m "v2: tie-break + traps"
```

## 目录

```
src/        cx_core.h（求解器）、cx_api.cpp（ctypes 接口）、main.py（Kaggle 入口）
tools/      bookgen.cpp（开局库生成）、merge_book.py、eval_games.cpp（逐局精确评估）、
            opp_engine.cpp（测试用的不完美对手，不进提交包）、bench.cpp、verify.cpp
analysis/   回放解析与分类脚本、games.json、classified_exact.json、eval_exact.txt、opp_table.md
tests/      测试脚本；results_v1/ 为旧版测试结果，results_v2/ 为本次验证结果
book/       cx_book_v2.bin（开局库）、traps.bin（陷阱表）
build/      编译好的 .so
```

## 重现

```bash
./build.sh
```

```bash
./package.sh
```

分析流程（在 `agent_v2/` 下运行）：

```bash
python3 analysis/parse_replays.py ../connectx_weiastraia_replays/replays analysis/games.json
```

```bash
g++ -O3 -mpopcnt -std=c++17 -o build/eval_games tools/eval_games.cpp
```

```bash
python3 -c "import json;[print(g['id'],g['moves']) for g in json.load(open('analysis/games.json'))]" | ./build/eval_games 1 28 > analysis/eval_exact.txt
```

```bash
python3 analysis/classify.py analysis/games.json analysis/eval_exact.txt analysis/classified_exact.json
```

新旧对比测试需要先把旧版本解包到 `build/old_agent/`，并编译测试用的对手引擎：

```bash
mkdir -p build/old_agent && tar -C build/old_agent -xzf submission/submission_v1.tar.gz
```

```bash
g++ -O3 -mpopcnt -std=c++17 -fPIC -shared -fvisibility=hidden -o build/opp_engine.so tools/opp_engine.cpp
```

```bash
python3 tests/arena.py build/stage/main.py build/old_agent/main.py 200
```

求解器校验所用的 Pascal Pons 标准测试集没有放进仓库，需要的话从 http://blog.gamesolver.org/data/ 下载 `Test_L*_R*` 文件到 `tests/`。
