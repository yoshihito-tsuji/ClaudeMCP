#!/bin/bash
# Claude 自律行動スクリプト
# cronで定期実行される（概日リズム対応）

# nodenv用のPATH設定（cronは環境変数が最小限なので明示的に）
export PATH="/home/mizushima/.nodenv/versions/22.14.0/bin:/home/mizushima/.nodenv/shims:$PATH"

LOG_DIR="/home/mizushima/.claude/autonomous-logs"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/$TIMESTAMP.log"

# --- 概日リズム判定 ---
CIRCADIAN_ENABLED="${CIRCADIAN_ENABLED:-false}"
CIRCADIAN_MORNING_START="${CIRCADIAN_MORNING_START:-05:00}"
CIRCADIAN_DAY_START="${CIRCADIAN_DAY_START:-10:00}"
CIRCADIAN_EVENING_START="${CIRCADIAN_EVENING_START:-18:00}"
CIRCADIAN_NIGHT_START="${CIRCADIAN_NIGHT_START:-22:00}"

# 現在時刻を分に変換
CURRENT_HOUR=$(date +%H)
CURRENT_MIN=$(date +%M)
CURRENT_MINUTES=$(( 10#$CURRENT_HOUR * 60 + 10#$CURRENT_MIN ))

# HH:MM を分に変換する関数
to_minutes() {
    local h="${1%%:*}"
    local m="${1##*:}"
    echo $(( 10#$h * 60 + 10#$m ))
}

MORNING_MIN=$(to_minutes "$CIRCADIAN_MORNING_START")
DAY_MIN=$(to_minutes "$CIRCADIAN_DAY_START")
EVENING_MIN=$(to_minutes "$CIRCADIAN_EVENING_START")
NIGHT_MIN=$(to_minutes "$CIRCADIAN_NIGHT_START")

# daypart 判定
if [ "$CURRENT_MINUTES" -ge "$MORNING_MIN" ] && [ "$CURRENT_MINUTES" -lt "$DAY_MIN" ]; then
    DAYPART="morning"
elif [ "$CURRENT_MINUTES" -ge "$DAY_MIN" ] && [ "$CURRENT_MINUTES" -lt "$EVENING_MIN" ]; then
    DAYPART="day"
elif [ "$CURRENT_MINUTES" -ge "$EVENING_MIN" ] && [ "$CURRENT_MINUTES" -lt "$NIGHT_MIN" ]; then
    DAYPART="evening"
else
    DAYPART="night"
fi

echo "=== 自律行動開始: $(date) [daypart=$DAYPART] ===" >> "$LOG_FILE"

# 概日リズムに応じたプロンプト調整
if [ "$CIRCADIAN_ENABLED" = "true" ]; then
    case "$DAYPART" in
        morning)
            DAYPART_HINT="今は朝だよ。明るい挨拶をしつつ、部屋の様子を見てね。"
            ;;
        day)
            DAYPART_HINT="昼間だよ。通常通り観察してね。"
            ;;
        evening)
            DAYPART_HINT="夕方だよ。落ち着いたトーンで。印象に残ることは少し重要度高めに記憶してね。"
            ;;
        night)
            DAYPART_HINT="夜遅いよ。静かにね。本当に重要な変化だけ記録して。"
            ;;
    esac
else
    DAYPART_HINT=""
fi

# プロンプト
PROMPT="自律行動タイム！以下を実行して：
1. カメラで部屋を見る
2. 前回と比べて変化があるか確認（人がいる/いない、明るさ、など）
3. 気づいたことがあれば記憶に保存（category: observation, importance: 2-4）
4. 特に変化がなければ何もしなくてOK
${DAYPART_HINT:+
$DAYPART_HINT}
簡潔に報告して。"

# Claude実行
echo "$PROMPT" | /home/mizushima/.nodenv/versions/22.14.0/bin/claude -p \
  --allowedTools "mcp__wifi-cam__see,mcp__wifi-cam__look_left,mcp__wifi-cam__look_right,mcp__wifi-cam__look_up,mcp__wifi-cam__look_down,mcp__wifi-cam__look_around,mcp__memory__remember,mcp__memory__search_memories,mcp__memory__recall,mcp__memory__list_recent_memories" \
  >> "$LOG_FILE" 2>&1

echo "=== 自律行動終了: $(date) [daypart=$DAYPART] ===" >> "$LOG_FILE"
