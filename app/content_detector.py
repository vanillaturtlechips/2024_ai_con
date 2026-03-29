from typing import Dict, List, Tuple, Optional
import json
import logging
from datetime import datetime
import re
import os

class ToxicContentDetector:
    def __init__(self, json_path: str):
        self.json_path = json_path
        self._setup_logging()
        self.toxic_data = self._load_toxic_data()
        print(f"데이터 로드 완료: {len(self.toxic_data)}개 항목")

    def _setup_logging(self):
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file = os.path.join(log_dir, 'content_filter.txt')
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )
        self.logger = logging.getLogger(__name__)

    def _load_toxic_data(self) -> List[Dict]:
        try:
            with open(self.json_path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
                return [entry for entry in data if self._is_valid_entry(entry)]
        except Exception as e:
            print(f"데이터 로딩 중 오류: {str(e)}")
            return []

    def check_content(self, text: str) -> Tuple[bool, Dict]:
        try:
            if not text or len(text.strip()) < 2:
                return False, self._create_result(False, set(), [])

            # 기본 금지어 검사
            basic_result = self._check_basic_toxic_words(text)
            if basic_result["is_toxic"]:
                self._log_toxic_content(text, basic_result)
                return True, basic_result

            # 고급 패턴 검사
            toxic_matches = []
            toxic_categories = set()
            text_lower = text.lower()

            for entry in self.toxic_data:
                # 유해성 점수가 2 이상인 항목만 검사
                if not any(entry.get(cat, 0) >= 2 for cat in ["욕설", "성혐오", "모욕", "외설", "폭력위협/범죄조장"]):
                    continue

                emphasized = self._get_emphasized_parts(entry)
                
                for part in emphasized:
                    part = part.strip().lower()
                    if not self._is_valid_toxic_pattern(part):
                        continue

                    # 정확한 단어 매칭을 위한 정규식 패턴
                    pattern = rf'\b{re.escape(part)}\b'
                    if re.search(pattern, text_lower):
                        category = self._determine_category(entry)
                        if category:
                            toxic_categories.add(category)
                            toxic_matches.append({
                                'matched_text': part,
                                'category': category,
                                'context': self._get_surrounding_context(text, part)
                            })

            result = self._create_result(bool(toxic_matches), toxic_categories, toxic_matches)
            if result["is_toxic"]:
                self._log_toxic_content(text, result)
            
            return result["is_toxic"], result

        except Exception as e:
            error_msg = f"콘텐츠 검사 중 오류: {str(e)}"
            self.logger.error(error_msg)
            return False, {"error": error_msg}

    def _get_emphasized_parts(self, entry: Dict) -> List[str]:
        """강조된 부분 추출"""
        highlighted = entry.get("대상하이라이트", "").strip()
        if not highlighted:
            return []
        return re.findall(r"''(.*?)''", highlighted)

    def _check_basic_toxic_words(self, text: str) -> Dict:
        basic_toxic_words = {
            "씨발", "병신", "개새끼", "지랄", "니미", "좆", "새끼",
            "미친", "죽여"
        }
        
        matches = []
        text_lower = text.lower()
        
        for word in basic_toxic_words:
            pattern = rf'\b{re.escape(word)}\b'
            if re.search(pattern, text_lower):
                matches.append({
                    'matched_text': word,
                    'category': "욕설/비속어",
                    'context': self._get_surrounding_context(text, word)
                })
        
        return self._create_result(bool(matches), {"욕설/비속어"} if matches else set(), matches)

    def _is_valid_toxic_pattern(self, pattern: str) -> bool:
        """유해 패턴 유효성 검사"""
        if not pattern or len(pattern.strip()) < 2:
            return False

        safe_patterns = {
            "좋은", "감사", "행복", "사랑", "축하", "건강", "화이팅", "파이팅", 
            "보내", "좋다", "좋아", "감사", "희망", "긍정", "노력", "열심히",
            "하루", "안녕", "반가", "환영", "수고", "화이팅", "파이팅"
        }
        
        pattern = pattern.lower()
        return (
            pattern not in safe_patterns and
            not any(safe.lower() in pattern.lower() for safe in safe_patterns)
        )

    def _is_valid_entry(self, entry: Dict) -> bool:
        if not isinstance(entry, dict):
            return False
            
        if "대상하이라이트" not in entry or not entry.get("대상하이라이트"):
            return False

        # 최소 하나의 카테고리가 2점 이상
        categories = ["욕설", "성혐오", "모욕", "외설", "폭력위협/범죄조장"]
        return any(entry.get(cat, 0) >= 2 for cat in categories)

    def _determine_category(self, entry: Dict) -> Optional[str]:
        category_map = {
            "욕설": ("욕설/비속어", 2),
            "성혐오": ("성차별", 2),
            "모욕": ("모욕", 2),
            "외설": ("외설", 2),
            "폭력위협/범죄조장": ("폭력/범죄", 2)
        }
        
        max_score = 0
        selected_category = None
        
        for db_category, (display_category, threshold) in category_map.items():
            score = entry.get(db_category, 0)
            if score >= threshold and score > max_score:
                max_score = score
                selected_category = display_category
                
        return selected_category

    def _get_surrounding_context(self, text: str, matched_word: str, context_words: int = 3) -> str:
        words = text.split()
        try:
            for i, word in enumerate(words):
                if matched_word.lower() in word.lower():
                    start = max(0, i - context_words)
                    end = min(len(words), i + context_words + 1)
                    return " ".join(words[start:end])
        except:
            return matched_word
        return matched_word

    def _create_result(self, is_toxic: bool, categories: set, matches: List[Dict]) -> Dict:
        return {
            "is_toxic": is_toxic,
            "categories": sorted(list(categories)),
            "matches": matches,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _log_toxic_content(self, text: str, result: Dict):
        log_message = f"\n{'=' * 50}\n"
        log_message += f"검사 시간: {result['timestamp']}\n"
        log_message += f"입력 텍스트: {text}\n"
        
        if result['categories']:
            log_message += f"감지된 카테고리: {', '.join(result['categories'])}\n"
            log_message += "감지된 패턴:\n"
            for match in result['matches']:
                log_message += f"- {match['category']}: {match['matched_text']}\n"
                log_message += f"  문맥: {match['context']}\n"
        else:
            log_message += "감지된 유해 콘텐츠 없음\n"
            
        log_message += "=" * 50
        self.logger.info(log_message)

class ContentFilter:
    def __init__(self, json_path: str, api_key: str = None):
        self.detector = ToxicContentDetector(json_path)
        print("ContentFilter 초기화 완료")

    def analyze_content(self, text: str) -> Tuple[bool, Dict]:
        return self.detector.check_content(text)