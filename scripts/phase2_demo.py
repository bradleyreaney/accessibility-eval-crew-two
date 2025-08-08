"""
Phase 2 Demo: Core Agent Evaluation System
References: Master Plan - Phase 2 Demo, Agent Integration Testing
"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.config.llm_config import LLMManager
from src.tools.pdf_parser import PDFParser
from src.agents.judge_agent import PrimaryJudgeAgent, SecondaryJudgeAgent
from src.agents.scoring_agent import ScoringAgent
from src.agents.analysis_agent import AnalysisAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Phase2Demo:
    """
    Demonstration of Phase 2 agent-based evaluation system.
    
    This demo showcases:
    - Judge agent evaluations (Primary and Secondary)
    - Scoring agent analysis and rankings
    - Analysis agent strategic recommendations
    - Complete workflow integration
    """
    
    def __init__(self):
        """Initialize the Phase 2 demo environment"""
        self.data_dir = Path(__file__).parent.parent / "data"
        self.audit_reports_dir = self.data_dir / "audit-reports"
        self.remediation_plans_dir = self.data_dir / "remediation-plans"
        
        # Initialize components
        self.llm_manager = None
        self.pdf_parser = PDFParser()
        self.agents = {}
        
        # Results storage
        self.audit_content = ""
        self.plan_contents = {}
        self.evaluations = []
        self.scoring_results = {}
        self.strategic_analysis = {}
    
    def setup(self) -> bool:
        """Setup the demo environment and validate components"""
        try:
            logger.info("🚀 Setting up Phase 2 Agent Demo...")
            
            # Initialize LLM Manager
            logger.info("Initializing LLM connections...")
            from src.config.llm_config import LLMConfig
            
            # Create a minimal config for demo (API keys would come from environment)
            config = LLMConfig(
                gemini_api_key=os.getenv("GOOGLE_API_KEY", "demo_key"),
                openai_api_key=os.getenv("OPENAI_API_KEY", "demo_key")
            )
            self.llm_manager = LLMManager(config)
            
            # Initialize agents
            logger.info("Initializing evaluation agents...")
            self.agents = {
                'primary_judge': PrimaryJudgeAgent(self.llm_manager),
                'secondary_judge': SecondaryJudgeAgent(self.llm_manager),
                'scoring_agent': ScoringAgent(self.llm_manager),
                'analysis_agent': AnalysisAgent(self.llm_manager)
            }
            
            # Load data
            logger.info("Loading audit reports and remediation plans...")
            self._load_data()
            
            logger.info("✅ Phase 2 demo setup completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Demo setup failed: {e}")
            return False
    
    def _load_data(self):
        """Load audit reports and remediation plans"""
        # Load audit report
        audit_file = self.audit_reports_dir / "AccessibilityReportTOA.pdf"
        if audit_file.exists():
            audit_doc = self.pdf_parser.parse_audit_report(audit_file)
            self.audit_content = audit_doc.content
            logger.info(f"Loaded audit report: {len(self.audit_content)} characters")
        else:
            logger.warning(f"Audit report not found: {audit_file}")
            self.audit_content = "Sample audit report content for demo purposes."
        
        # Load remediation plans (limit to first 3 for demo)
        plan_files = list(self.remediation_plans_dir.glob("Plan*.pdf"))[:3]
        
        for plan_file in plan_files:
            try:
                plan_doc = self.pdf_parser.parse_remediation_plan(plan_file)
                plan_name = plan_file.stem
                self.plan_contents[plan_name] = plan_doc.content
                logger.info(f"Loaded {plan_name}: {len(plan_doc.content)} characters")
            except Exception as e:
                logger.warning(f"Failed to load {plan_file.name}: {e}")
                # Use sample content for demo if file loading fails
                self.plan_contents[plan_file.stem] = f"Sample content for {plan_file.stem} - accessibility remediation plan with comprehensive approach."
        
        logger.info(f"Loaded {len(self.plan_contents)} remediation plans for evaluation")
    
    def run_judge_evaluations(self) -> List[Dict[str, Any]]:
        """Run primary and secondary judge evaluations on all plans"""
        logger.info("🎯 Starting Judge Agent Evaluations...")
        
        evaluations = []
        
        for plan_name, plan_content in self.plan_contents.items():
            logger.info(f"\n📋 Evaluating {plan_name}...")
            
            # Primary judge evaluation
            logger.info("Primary Judge (Gemini Pro) evaluating...")
            primary_eval = self.agents['primary_judge'].evaluate_plan(
                plan_name, plan_content, self.audit_content
            )
            evaluations.append(primary_eval)
            
            if primary_eval['success']:
                logger.info(f"✅ Primary evaluation completed for {plan_name}")
                self._print_evaluation_summary(primary_eval)
            else:
                logger.error(f"❌ Primary evaluation failed for {plan_name}")
            
            # Secondary judge evaluation
            logger.info("Secondary Judge (GPT-4) evaluating...")
            secondary_eval = self.agents['secondary_judge'].evaluate_plan(
                plan_name, plan_content, self.audit_content,
                primary_eval.get('evaluation_content', '')
            )
            evaluations.append(secondary_eval)
            
            if secondary_eval['success']:
                logger.info(f"✅ Secondary evaluation completed for {plan_name}")
                self._print_evaluation_summary(secondary_eval)
            else:
                logger.error(f"❌ Secondary evaluation failed for {plan_name}")
        
        self.evaluations = evaluations
        logger.info(f"\n🎯 Judge evaluations completed: {len(evaluations)} total evaluations")
        return evaluations
    
    def run_scoring_analysis(self) -> Dict[str, Any]:
        """Run scoring agent analysis on all evaluations"""
        logger.info("\n📊 Starting Scoring Agent Analysis...")
        
        # Define evaluation criteria weights
        criteria_weights = {
            'Strategic Prioritization': 0.4,
            'Technical Specificity': 0.3,
            'Comprehensiveness': 0.2,
            'Long-term Vision': 0.1
        }
        
        # Calculate final scores
        scoring_results = self.agents['scoring_agent'].calculate_final_scores(
            self.evaluations, criteria_weights
        )
        
        if scoring_results['success']:
            logger.info("✅ Scoring analysis completed successfully")
            self._print_scoring_summary(scoring_results)
        else:
            logger.error("❌ Scoring analysis failed")
        
        self.scoring_results = scoring_results
        return scoring_results
    
    def run_strategic_analysis(self) -> Dict[str, Any]:
        """Run strategic analysis agent on evaluation results"""
        logger.info("\n🎯 Starting Strategic Analysis...")
        
        # Generate strategic analysis
        strategic_analysis = self.agents['analysis_agent'].generate_strategic_analysis(
            self.evaluations, self.scoring_results
        )
        
        if strategic_analysis['success']:
            logger.info("✅ Strategic analysis completed successfully")
            self._print_strategic_summary(strategic_analysis)
        else:
            logger.error("❌ Strategic analysis failed")
        
        # Generate executive summary
        logger.info("\n📋 Generating Executive Summary...")
        all_data = {
            'evaluations': self.evaluations,
            'scoring': self.scoring_results,
            'strategic_analysis': strategic_analysis
        }
        
        executive_summary = self.agents['analysis_agent'].generate_executive_summary(all_data)
        
        if executive_summary['success']:
            logger.info("✅ Executive summary generated successfully")
            self._print_executive_summary(executive_summary)
        
        self.strategic_analysis = strategic_analysis
        return strategic_analysis
    
    def run_complete_demo(self):
        """Run the complete Phase 2 demonstration"""
        logger.info("🌟 Starting Complete Phase 2 Agent Demo")
        logger.info("=" * 60)
        
        # Setup
        if not self.setup():
            logger.error("Demo setup failed. Exiting.")
            return
        
        # Phase 1: Judge Evaluations
        evaluations = self.run_judge_evaluations()
        if not evaluations:
            logger.error("No evaluations completed. Exiting demo.")
            return
        
        # Phase 2: Scoring Analysis
        scoring_results = self.run_scoring_analysis()
        if not scoring_results.get('success'):
            logger.error("Scoring analysis failed. Continuing with available data.")
        
        # Phase 3: Strategic Analysis
        strategic_analysis = self.run_strategic_analysis()
        
        # Demo Summary
        self._print_demo_summary()
        
        logger.info("\n🌟 Phase 2 Agent Demo Completed Successfully!")
        logger.info("=" * 60)
    
    def _print_evaluation_summary(self, evaluation: Dict[str, Any]):
        """Print a summary of an evaluation result"""
        evaluator = evaluation.get('evaluator', 'Unknown')
        plan_name = evaluation.get('plan_name', 'Unknown')
        content_preview = str(evaluation.get('evaluation_content', ''))[:200]
        
        print(f"    {evaluator} - {plan_name}")
        print(f"    Preview: {content_preview}...")
        print()
    
    def _print_scoring_summary(self, scoring_results: Dict[str, Any]):
        """Print a summary of scoring results"""
        print("\n📊 SCORING RESULTS:")
        print("-" * 40)
        
        rankings = scoring_results.get('rankings', [])
        for i, (plan_name, score) in enumerate(rankings, 1):
            print(f"  {i}. {plan_name}: {score:.2f}/10")
        
        print(f"\nMethod: {scoring_results.get('scoring_method', 'Unknown')}")
        print(f"Evaluations Processed: {scoring_results.get('evaluations_processed', 0)}")
    
    def _print_strategic_summary(self, strategic_analysis: Dict[str, Any]):
        """Print a summary of strategic analysis"""
        print("\n🎯 STRATEGIC ANALYSIS:")
        print("-" * 40)
        
        recommendation = strategic_analysis.get('primary_recommendation', 'See full analysis')
        print(f"Primary Recommendation: {recommendation}")
        
        analysis_preview = str(strategic_analysis.get('analysis_content', ''))[:300]
        print(f"\nAnalysis Preview: {analysis_preview}...")
    
    def _print_executive_summary(self, executive_summary: Dict[str, Any]):
        """Print the executive summary"""
        print("\n📋 EXECUTIVE SUMMARY:")
        print("-" * 40)
        
        summary_content = executive_summary.get('summary_content', '')
        if isinstance(summary_content, str):
            print(summary_content[:500] + "..." if len(summary_content) > 500 else summary_content)
        else:
            print("Summary content not available in expected format")
    
    def _print_demo_summary(self):
        """Print overall demo summary"""
        print("\n" + "=" * 60)
        print("                    DEMO SUMMARY")
        print("=" * 60)
        
        print(f"✅ Agents Initialized: {len(self.agents)}")
        print(f"✅ Plans Evaluated: {len(self.plan_contents)}")
        print(f"✅ Total Evaluations: {len(self.evaluations)}")
        print(f"✅ Scoring Analysis: {'Completed' if self.scoring_results.get('success') else 'Failed'}")
        print(f"✅ Strategic Analysis: {'Completed' if self.strategic_analysis.get('success') else 'Failed'}")
        
        # Show agent capabilities
        print("\n🤖 AGENT CAPABILITIES DEMONSTRATED:")
        for agent_name, agent in self.agents.items():
            info = agent.get_agent_info()
            print(f"  • {info['name']} ({info['llm']})")
            for capability in info['capabilities'][:2]:  # Show first 2 capabilities
                print(f"    - {capability}")
    
    def test_individual_components(self):
        """Test individual components in isolation"""
        logger.info("\n🔧 Testing Individual Components...")
        
        if not self.setup():
            return
        
        # Test tools
        logger.info("Testing agent tools...")
        from src.agents.tools.evaluation_framework import EvaluationFrameworkTool
        from src.agents.tools.scoring_calculator import ScoringCalculatorTool
        
        eval_tool = EvaluationFrameworkTool()
        scoring_tool = ScoringCalculatorTool()
        
        # Quick tool tests
        if hasattr(eval_tool, 'criteria_weights'):
            logger.info(f"✅ Evaluation framework loaded with {len(eval_tool.criteria_weights)} criteria")
        
        logger.info("✅ Individual component testing completed")


def main():
    """Run the Phase 2 demonstration"""
    demo = Phase2Demo()
    
    # Option 1: Run complete demo
    demo.run_complete_demo()
    
    # Option 2: Test individual components (uncomment to run)
    # demo.test_individual_components()


if __name__ == "__main__":
    main()
