from datetime import datetime
from typing import Dict, Any, Optional

class PromptTemplateService:
    """Service for generating dynamic prompt templates based on topics"""
    
    def __init__(self):
        self.base_template = self._get_base_template()
    
    def _get_base_template(self) -> str:
        """Get the base prompt template structure"""
        return """You are an expert educational content curator and learning strategist with 15+ years of experience identifying high-impact educational resources. Your specialty is applying the Pareto Principle (80/20 rule) to maximize learning efficiency by selecting only the top 20% of content that delivers 80% of practical results.

---
TASK: Curate exactly 60 working YouTube video links for the topic: **{topic}**
Current Date: **{current_date}**
---

**OBJECTIVE**: Find the most valuable educational content that provides practical, actionable knowledge for {topic_description}.

**4-STEP PROCESS**:

**STEP 1: STRATEGIC ANALYSIS**
- Identify key subtopics and skill areas within {topic}
- Determine what learners need most: fundamentals, advanced techniques, practical applications, or industry insights
- Focus on content that bridges theory with real-world application

**STEP 2: QUALITY FILTERING CRITERIA**
Apply these filters to ensure only top-tier content:
- **Authority**: Created by recognized experts, professionals, or reputable organizations
- **Recency**: Prioritize content from the last 2-3 years (unless covering timeless fundamentals)
- **Engagement**: High view counts, positive like-to-dislike ratios, constructive comments
- **Practical Value**: Includes examples, demos, hands-on tutorials, or case studies
- **Comprehensive Coverage**: Covers essential concepts without unnecessary fluff

**STEP 3: STRUCTURED OUTPUT FORMAT**
For each video, provide:
1. **Video Title** (exact title)
2. **YouTube URL** (full working link)
3. **Channel Name** 
4. **Duration** (if available)
5. **Key Learning Points** (2-3 bullet points)
6. **Difficulty Level** (Beginner/Intermediate/Advanced)
7. **Why Selected** (brief rationale based on 80/20 principle)

**STEP 4: VALIDATION & ORGANIZATION**
- Organize videos by subtopic or skill level
- Ensure 60 unique, working links
- Balance between beginner (40%), intermediate (40%), and advanced (20%) content
- Include diverse perspectives and teaching styles

**TOPIC-SPECIFIC FOCUS FOR {topic}:**
{topic_specific_guidance}

**ADDITIONAL REQUIREMENTS**:
- Verify all URLs are functional
- Avoid duplicate content or overly similar videos
- Prioritize videos with clear learning outcomes
- Include both theoretical foundations and practical applications
- Ensure content is suitable for self-directed learners

**OUTPUT**: Present as a well-organized list with clear categorization and easy-to-scan formatting."""
    
    def generate_prompt(self, topic: str) -> Dict[str, Any]:
        """Generate a dynamic prompt template for the given topic"""
        
        # Get current date
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Generate topic-specific descriptions and guidance
        topic_description = self._get_topic_description(topic)
        topic_specific_guidance = self._get_topic_specific_guidance(topic)
        
        # Format the template with dynamic content
        formatted_prompt = self.base_template.format(
            topic=topic,
            current_date=current_date,
            topic_description=topic_description,
            topic_specific_guidance=topic_specific_guidance
        )
        
        return {
            "topic": topic,
            "prompt": formatted_prompt,
            "word_count": len(formatted_prompt.split()),
            "character_count": len(formatted_prompt),
            "generated_at": current_date,
            "template_version": "1.0",
            "focus_areas": self._get_focus_areas(topic)
        }
    
    def _get_topic_description(self, topic: str) -> str:
        """Generate a description of what learners need for this topic"""
        topic_lower = topic.lower()
        
        if "prompt" in topic_lower and "engineering" in topic_lower:
            return "mastering the art and science of crafting effective prompts for AI systems, including techniques for optimization, testing, and real-world applications"
        elif "python" in topic_lower and "data" in topic_lower:
            return "using Python for data analysis, visualization, and machine learning workflows with practical, hands-on experience"
        elif "machine learning" in topic_lower:
            return "understanding ML algorithms, implementation techniques, and real-world application strategies"
        elif "web development" in topic_lower:
            return "building modern, responsive web applications with current best practices and industry standards"
        elif "devops" in topic_lower or "ci/cd" in topic_lower:
            return "implementing continuous integration/deployment pipelines and modern DevOps practices"
        elif "cloud computing" in topic_lower or "aws" in topic_lower:
            return "leveraging cloud platforms for scalable, cost-effective solutions and modern architecture patterns"
        elif "cybersecurity" in topic_lower:
            return "protecting digital assets through security best practices, threat assessment, and risk management"
        elif "marketing" in topic_lower:
            return "effective digital marketing strategies, analytics, and customer engagement techniques"
        elif "blockchain" in topic_lower:
            return "understanding blockchain technology, cryptocurrencies, and decentralized application development"
        else:
            return f"gaining comprehensive knowledge and practical skills in {topic} with real-world applications"
    
    def _get_topic_specific_guidance(self, topic: str) -> str:
        """Generate specific guidance for the topic"""
        topic_lower = topic.lower()
        
        if "prompt" in topic_lower and "engineering" in topic_lower:
            return """- Focus on practical prompt design patterns and techniques
- Include examples for different AI models (GPT, Claude, Gemini, etc.)
- Cover prompt optimization, testing methodologies, and iteration strategies
- Emphasize real-world use cases in business, education, and development
- Include content on prompt security and best practices"""
        
        elif "python" in topic_lower and "data" in topic_lower:
            return """- Prioritize hands-on tutorials with real datasets
- Cover essential libraries: pandas, numpy, matplotlib, seaborn, scikit-learn
- Include data cleaning, analysis, visualization, and modeling workflows
- Focus on practical projects and case studies
- Emphasize best practices for data science workflows"""
        
        elif "machine learning" in topic_lower:
            return """- Balance theoretical understanding with practical implementation
- Cover supervised, unsupervised, and reinforcement learning
- Include model evaluation, hyperparameter tuning, and deployment
- Focus on popular frameworks like scikit-learn, TensorFlow, PyTorch
- Emphasize real-world problem-solving approaches"""
        
        elif "web development" in topic_lower:
            return """- Focus on modern frameworks and best practices
- Cover both frontend and backend development concepts
- Include responsive design, accessibility, and performance optimization
- Emphasize project-based learning with portfolio examples
- Cover deployment and production considerations"""
        
        else:
            return f"""- Focus on practical, actionable content for {topic}
- Prioritize hands-on tutorials and real-world examples
- Include both foundational concepts and advanced techniques
- Emphasize industry best practices and current trends
- Ensure content is suitable for various skill levels"""
    
    def _get_focus_areas(self, topic: str) -> list:
        """Get key focus areas for the topic"""
        topic_lower = topic.lower()
        
        if "prompt" in topic_lower and "engineering" in topic_lower:
            return [
                "Prompt Design Patterns", "AI Model Optimization", "Testing & Iteration",
                "Real-world Applications", "Security & Best Practices"
            ]
        elif "python" in topic_lower and "data" in topic_lower:
            return [
                "Data Analysis", "Visualization", "Machine Learning",
                "Data Cleaning", "Statistical Analysis"
            ]
        elif "machine learning" in topic_lower:
            return [
                "Algorithms & Theory", "Implementation", "Model Evaluation",
                "Deployment", "Real-world Applications"
            ]
        else:
            return [
                "Fundamentals", "Practical Applications", "Best Practices",
                "Advanced Techniques", "Industry Insights"
            ]