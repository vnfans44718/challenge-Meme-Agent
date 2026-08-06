"""감정 분류기(classify_emotion)의 정확도를 평가 데이터셋으로 측정한다.

실제 Anthropic API를 호출하므로 비용/시간이 들어 pytest 스위트(mock 기반)와는
별도로 둔다. 실행: poetry run python evals/run_eval.py
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent.services.emotion_classifier import EMOTION_LABELS, classify_emotion  # noqa: E402
from dataset import EVAL_DATASET  # noqa: E402


def run() -> None:
    correct = 0
    confusion = {actual: Counter() for actual in EMOTION_LABELS}
    wrong = []

    for text, expected in EVAL_DATASET:
        predicted = classify_emotion(text)
        confusion[expected][predicted] += 1
        if predicted == expected:
            correct += 1
        else:
            wrong.append((text, expected, predicted))

    total = len(EVAL_DATASET)
    accuracy = correct / total * 100
    print(f"\n정확도: {correct}/{total} ({accuracy:.1f}%)\n")

    print("혼동 행렬 (행=실제 라벨, 열=예측 라벨)")
    print("        " + " ".join(f"{l:>6}" for l in EMOTION_LABELS))
    for actual in EMOTION_LABELS:
        row = " ".join(f"{confusion[actual][pred]:>6}" for pred in EMOTION_LABELS)
        print(f"{actual:>6}  {row}")

    if wrong:
        print(f"\n오답 {len(wrong)}건:")
        for text, expected, predicted in wrong:
            print(f"  [{expected} → {predicted}] {text}")


if __name__ == "__main__":
    run()
