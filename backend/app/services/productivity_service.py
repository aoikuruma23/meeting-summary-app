from typing import Dict, List, Optional
import json
from datetime import datetime

class ProductivityService:
    """会議効率性を分析するサービス"""
    
    def __init__(self):
        self.efficiency_weights = {
            'time_efficiency': 0.3,      # 時間効率（予定時間 vs 実際時間）
            'participation_rate': 0.25,   # 参加率（発言した参加者数 / 総参加者数）
            'decision_efficiency': 0.2,   # 決定効率（決定事項数 / 議題数）
            'action_completion': 0.15,    # アクション完了率
            'topic_coverage': 0.1         # 議題カバー率
        }
    
    def calculate_meeting_efficiency(self, meeting_data: Dict) -> Dict:
        """会議効率性を計算"""
        scores = {}
        
        # 時間効率の計算
        if meeting_data.get('scheduled_duration') and meeting_data.get('actual_duration'):
            scheduled = meeting_data['scheduled_duration']
            actual = meeting_data['actual_duration']
            if scheduled > 0:
                time_ratio = min(actual / scheduled, 2.0)  # 最大2倍まで
                scores['time_efficiency'] = max(0, 100 - (time_ratio - 1) * 50)
            else:
                scores['time_efficiency'] = 50  # デフォルト値
        else:
            scores['time_efficiency'] = 50
        
        # 参加率の計算
        if meeting_data.get('participant_count') and meeting_data.get('speakers'):
            total_participants = meeting_data['participant_count']
            active_speakers = len(meeting_data['speakers'])
            if total_participants > 0:
                scores['participation_rate'] = min(100, (active_speakers / total_participants) * 100)
            else:
                scores['participation_rate'] = 50
        else:
            scores['participation_rate'] = 50
        
        # 決定効率の計算
        if meeting_data.get('topic_count') and meeting_data.get('decision_count'):
            topics = meeting_data['topic_count']
            decisions = meeting_data['decision_count']
            if topics > 0:
                scores['decision_efficiency'] = min(100, (decisions / topics) * 100)
            else:
                scores['decision_efficiency'] = 50
        else:
            scores['decision_efficiency'] = 50
        
        # アクション完了率の計算
        if meeting_data.get('action_item_count'):
            action_items = meeting_data['action_item_count']
            # 仮の完了率（実際の実装では完了済みアクション数を追跡する必要がある）
            scores['action_completion'] = 70  # デフォルト値
        else:
            scores['action_completion'] = 50
        
        # 議題カバー率の計算
        if meeting_data.get('topic_count') and meeting_data.get('completed_topics'):
            total_topics = meeting_data['topic_count']
            completed_topics = meeting_data['completed_topics']
            if total_topics > 0:
                scores['topic_coverage'] = min(100, (completed_topics / total_topics) * 100)
            else:
                scores['topic_coverage'] = 50
        else:
            scores['topic_coverage'] = 50
        
        # 総合スコアの計算
        total_score = sum(
            scores[key] * self.efficiency_weights[key]
            for key in self.efficiency_weights.keys()
        )
        
        efficiency_level = self._get_efficiency_level(total_score)
        
        return {
            'overall_score': round(total_score, 1),
            'efficiency_level': efficiency_level,
            'detailed_scores': scores,
            'recommendations': self._generate_recommendations(scores, meeting_data)
        }
    
    def _get_efficiency_level(self, score: float) -> str:
        """効率性レベルを判定"""
        if score >= 80:
            return "優秀"
        elif score >= 60:
            return "良好"
        elif score >= 40:
            return "普通"
        else:
            return "改善が必要"
    
    def _generate_recommendations(self, scores: Dict, meeting_data: Dict) -> List[str]:
        """改善提案を生成"""
        recommendations = []
        
        if scores.get('time_efficiency', 100) < 60:
            recommendations.append("会議時間の管理を改善してください。アジェンダを明確にし、時間配分を事前に決めておくことをお勧めします。")
        
        if scores.get('participation_rate', 100) < 60:
            recommendations.append("参加者の発言機会を増やしてください。全員が発言できるよう、ファシリテーションを改善することをお勧めします。")
        
        if scores.get('decision_efficiency', 100) < 60:
            recommendations.append("決定事項を明確にしてください。議題ごとに結論を出すことをお勧めします。")
        
        if scores.get('action_completion', 100) < 60:
            recommendations.append("アクションアイテムの進捗管理を強化してください。担当者と期限を明確にし、フォローアップを定期的に行うことをお勧めします。")
        
        if scores.get('topic_coverage', 100) < 60:
            recommendations.append("議題の完了率を向上させてください。優先順位をつけて、重要な議題から処理することをお勧めします。")
        
        if not recommendations:
            recommendations.append("会議は効率的に進行されています。この調子で継続してください。")
        
        return recommendations
    
    def analyze_speaker_contribution(self, speakers_data: List[Dict]) -> Dict:
        """参加者の貢献度を分析"""
        if not speakers_data:
            return {"error": "話者データがありません"}
        
        total_utterances = sum(len(speaker.get('utterances', [])) for speaker in speakers_data)
        total_duration = sum(
            sum(utt.get('end', 0) - utt.get('start', 0) for utt in speaker.get('utterances', []))
            for speaker in speakers_data
        )
        
        speaker_analysis = []
        for speaker in speakers_data:
            utterances = speaker.get('utterances', [])
            speaker_duration = sum(utt.get('end', 0) - utt.get('start', 0) for utt in utterances)
            
            contribution = {
                'speaker_id': speaker.get('id'),
                'name': speaker.get('name'),
                'utterance_count': len(utterances),
                'total_duration': round(speaker_duration, 2),
                'contribution_percentage': round((len(utterances) / total_utterances * 100), 1) if total_utterances > 0 else 0,
                'duration_percentage': round((speaker_duration / total_duration * 100), 1) if total_duration > 0 else 0,
                'average_utterance_length': round(speaker_duration / len(utterances), 2) if utterances else 0
            }
            speaker_analysis.append(contribution)
        
        # 貢献度でソート
        speaker_analysis.sort(key=lambda x: x['contribution_percentage'], reverse=True)
        
        return {
            'total_utterances': total_utterances,
            'total_duration': round(total_duration, 2),
            'speaker_analysis': speaker_analysis,
            'most_active_speaker': speaker_analysis[0] if speaker_analysis else None,
            'least_active_speaker': speaker_analysis[-1] if speaker_analysis else None
        } 