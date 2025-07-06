"""
AI Resume Enhancer Service
Uses Google Gemini API (Free tier) instead of paid services
"""

import google.generativeai as genai
import os
import logging
import time
from typing import Dict, List, Any, Optional
import json
import re

class AIEnhancer:
    """Enhance resumes using Google Gemini API (Free)"""

    def __init__(self):
        """Initialize with Gemini API"""
        self.setup_logging()
        self.setup_gemini()

    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def setup_gemini(self):
        """Setup Google Gemini API"""
        try:
            # Get API key from environment or Streamlit secrets
            api_key = os.getenv('GEMINI_API_KEY')

            if not api_key:
                try:
                    import streamlit as st
                    api_key = st.secrets.get('GEMINI_API_KEY')
                except:
                    pass

            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables or Streamlit secrets")

            # Configure Gemini
            genai.configure(api_key=api_key)

            # Use free Gemini model
            self.model = genai.GenerativeModel('gemini-1.5-flash')

            # Test the connection
            test_response = self.model.generate_content("Hello, test connection")
            self.logger.info("✅ Gemini API connected successfully")

            # Rate limiting for free tier
            self.rate_limit_delay = 2  # seconds between requests
            self.last_request_time = 0

        except Exception as e:
            self.logger.error(f"❌ Failed to setup Gemini API: {e}")
            self.model = None

    def _rate_limit(self):
        """Implement rate limiting for free tier"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def enhance_resume(self, content: str, entities: Dict) -> Dict[str, Any]:
        """Enhance resume content using Gemini AI"""
        if not self.model:
            return self._fallback_enhancement(content, entities)

        try:
            enhanced_resume = {
                'original_content': content,
                'enhanced_summary': self._enhance_summary(content, entities),
                'enhanced_skills': self._enhance_skills(entities.get('skills', [])),
                'enhanced_experience': self._enhance_experience(content, entities),
                'suggested_improvements': self._suggest_improvements(content, entities),
                'ats_optimizations': self._optimize_for_ats(content),
                'enhanced_full_content': ''
            }

            # Generate full enhanced content
            enhanced_resume['enhanced_full_content'] = self._generate_full_enhanced_resume(enhanced_resume)

            return enhanced_resume

        except Exception as e:
            self.logger.error(f"Enhancement failed: {e}")
            return self._fallback_enhancement(content, entities)

    def _enhance_summary(self, content: str, entities: Dict) -> str:
        """Enhance professional summary"""
        try:
            self._rate_limit()

            prompt = f"""
            You are a professional resume writer. Enhance the following resume content by creating a compelling professional summary.

            Original Resume Content:
            {content[:2000]}  # Limit content to avoid token limits

            Contact Info: {entities.get('contact_info', {})}
            Skills: {entities.get('skills', [])}
            Experience: {entities.get('experience', [])}

            Create a professional summary that:
            1. Highlights key strengths and achievements
            2. Is 3-4 sentences long
            3. Uses action verbs and quantifiable results
            4. Is tailored to the person's experience level
            5. Includes relevant keywords for ATS optimization

            Return only the enhanced professional summary, no additional text.
            """

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            self.logger.error(f"Summary enhancement failed: {e}")
            return self._fallback_summary(entities)

    def _enhance_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Enhance and categorize skills"""
        try:
            self._rate_limit()

            skills_text = ', '.join(skills) if skills else "No skills detected"

            prompt = f"""
            You are a career advisor. Analyze these skills and enhance them:

            Current Skills: {skills_text}

            Please:
            1. Add relevant missing skills that complement the existing ones
            2. Categorize skills into: Technical, Soft Skills, Industry-Specific, Tools/Software
            3. Suggest 3-5 additional skills that would be valuable
            4. Ensure skills are ATS-friendly and use standard terminology

            Return the response in this JSON format:
            {
                "technical": [],
                "soft_skills": [],
                "industry_specific": [],
                "tools_software": [],
                "suggested_additions": []
            }

            Return only valid JSON, no additional text.
            """

            response = self.model.generate_content(prompt)

            # Parse JSON response
            try:
                enhanced_skills = json.loads(response.text.strip())
                return enhanced_skills
            except json.JSONDecodeError:
                return self._fallback_skills_categorization(skills)

        except Exception as e:
            self.logger.error(f"Skills enhancement failed: {e}")
            return self._fallback_skills_categorization(skills)

    def _enhance_experience(self, content: str, entities: Dict) -> List[Dict]:
        """Enhance work experience descriptions"""
        try:
            self._rate_limit()

            experience = entities.get('experience', [])
            if not experience:
                return []

            prompt = f"""
            You are a professional resume writer. Enhance these work experience entries:

            Original Content: {content[:1500]}
            Current Experience: {experience}

            For each role, create enhanced descriptions that:
            1. Use strong action verbs
            2. Include quantifiable achievements where possible
            3. Are 2-3 bullet points each
            4. Show impact and results
            5. Use ATS-friendly keywords

            Return as JSON array with format:
            [
                {
                    "role": "job title",
                    "company": "company name",
                    "enhanced_description": ["bullet point 1", "bullet point 2", "bullet point 3"]
                }
            ]

            Return only valid JSON, no additional text.
            """

            response = self.model.generate_content(prompt)

            try:
                enhanced_exp = json.loads(response.text.strip())
                return enhanced_exp
            except json.JSONDecodeError:
                return self._fallback_experience_enhancement(experience)

        except Exception as e:
            self.logger.error(f"Experience enhancement failed: {e}")
            return self._fallback_experience_enhancement(entities.get('experience', []))

    def _suggest_improvements(self, content: str, entities: Dict) -> List[str]:
        """Suggest general improvements"""
        try:
            self._rate_limit()

            prompt = f"""
            You are a resume expert. Analyze this resume and suggest specific improvements:

            Resume Content: {content[:1500]}
            Extracted Entities: {str(entities)[:500]}

            Provide 5-7 specific, actionable improvement suggestions that:
            1. Address content gaps
            2. Improve ATS compatibility  
            3. Enhance professional presentation
            4. Strengthen impact statements
            5. Improve keyword optimization

            Format as a simple list, one suggestion per line starting with "•".
            Return only the suggestions, no additional text.
            """

            response = self.model.generate_content(prompt)
            suggestions = response.text.strip().split('\n')
            return [s.strip() for s in suggestions if s.strip()]

        except Exception as e:
            self.logger.error(f"Suggestions failed: {e}")
            return self._fallback_suggestions()

    def _optimize_for_ats(self, content: str) -> Dict[str, Any]:
        """Optimize content for ATS systems"""
        try:
            self._rate_limit()

            prompt = f"""
            You are an ATS optimization expert. Analyze this resume for ATS compatibility:

            Content: {content[:1500]}

            Provide specific ATS optimization recommendations including:
            1. Keywords that should be added
            2. Formatting improvements
            3. Section organization suggestions
            4. Common ATS red flags to avoid

            Return as JSON:
            {
                "keywords_to_add": [],
                "formatting_improvements": [],
                "organization_suggestions": [],
                "red_flags_found": [],
                "overall_ats_score": 0-100
            }

            Return only valid JSON, no additional text.
            """

            response = self.model.generate_content(prompt)

            try:
                ats_analysis = json.loads(response.text.strip())
                return ats_analysis
            except json.JSONDecodeError:
                return self._fallback_ats_optimization()

        except Exception as e:
            self.logger.error(f"ATS optimization failed: {e}")
            return self._fallback_ats_optimization()

    def _generate_full_enhanced_resume(self, enhanced_data: Dict) -> str:
        """Generate complete enhanced resume"""
        try:
            self._rate_limit()

            prompt = f"""
            Create a complete, professional resume using this enhanced data:

            Enhanced Summary: {enhanced_data.get('enhanced_summary', '')}
            Enhanced Skills: {enhanced_data.get('enhanced_skills', {})}
            Enhanced Experience: {enhanced_data.get('enhanced_experience', [])}

            Format as a clean, professional resume with:
            1. Professional Summary section
            2. Core Competencies/Skills section
            3. Professional Experience section
            4. Use consistent formatting
            5. ATS-friendly structure
            6. Action verbs and quantified achievements

            Return only the formatted resume content, no additional text.
            """

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            self.logger.error(f"Full resume generation failed: {e}")
            return self._fallback_full_resume(enhanced_data)

    def _fallback_enhancement(self, content: str, entities: Dict) -> Dict[str, Any]:
        """Fallback enhancement when AI is unavailable"""
        return {
            'original_content': content,
            'enhanced_summary': self._fallback_summary(entities),
            'enhanced_skills': self._fallback_skills_categorization(entities.get('skills', [])),
            'enhanced_experience': self._fallback_experience_enhancement(entities.get('experience', [])),
            'suggested_improvements': self._fallback_suggestions(),
            'ats_optimizations': self._fallback_ats_optimization(),
            'enhanced_full_content': content  # Return original if enhancement fails
        }

    def _fallback_summary(self, entities: Dict) -> str:
        """Fallback professional summary"""
        skills = entities.get('skills', [])
        experience = entities.get('experience', [])

        if skills and experience:
            return f"Experienced professional with expertise in {', '.join(skills[:3])}. Proven track record in {experience[0].get('role', 'various roles')} with strong analytical and problem-solving abilities. Committed to delivering high-quality results and driving organizational success."
        else:
            return "Dedicated professional with strong analytical and problem-solving skills. Committed to continuous learning and delivering excellent results in challenging environments."

    def _fallback_skills_categorization(self, skills: List[str]) -> Dict[str, List[str]]:
        """Fallback skills categorization"""
        technical_keywords = ['python', 'java', 'sql', 'javascript', 'html', 'css', 'react', 'node']
        soft_keywords = ['communication', 'leadership', 'teamwork', 'problem solving', 'management']

        technical = [s for s in skills if any(keyword in s.lower() for keyword in technical_keywords)]
        soft_skills = [s for s in skills if any(keyword in s.lower() for keyword in soft_keywords)]
        other = [s for s in skills if s not in technical and s not in soft_skills]

        return {
            'technical': technical,
            'soft_skills': soft_skills,
            'industry_specific': other,
            'tools_software': [],
            'suggested_additions': ['Problem Solving', 'Critical Thinking', 'Time Management']
        }

    def _fallback_experience_enhancement(self, experience: List[Dict]) -> List[Dict]:
        """Fallback experience enhancement"""
        enhanced = []
        for exp in experience:
            enhanced.append({
                'role': exp.get('role', 'Professional'),
                'company': exp.get('company', 'Organization'),
                'enhanced_description': [
                    f"Successfully performed {exp.get('role', 'professional duties')} responsibilities",
                    "Collaborated with cross-functional teams to achieve organizational goals",
                    "Contributed to process improvements and operational efficiency"
                ]
            })
        return enhanced

    def _fallback_suggestions(self) -> List[str]:
        """Fallback improvement suggestions"""
        return [
            "• Add quantifiable achievements with specific numbers and percentages",
            "• Include relevant keywords for your target industry",
            "• Ensure consistent formatting throughout the document",
            "• Add a professional summary at the top",
            "• Include both technical and soft skills",
            "• Use action verbs to start bullet points",
            "• Consider adding relevant certifications or training"
        ]

    def _fallback_ats_optimization(self) -> Dict[str, Any]:
        """Fallback ATS optimization"""
        return {
            'keywords_to_add': ['Leadership', 'Project Management', 'Data Analysis', 'Communication'],
            'formatting_improvements': ['Use standard fonts', 'Avoid graphics', 'Use simple bullet points'],
            'organization_suggestions': ['Add contact information at top', 'Use clear section headers'],
            'red_flags_found': ['Check for spelling errors', 'Ensure consistent formatting'],
            'overall_ats_score': 75
        }

    def _fallback_full_resume(self, enhanced_data: Dict) -> str:
        """Fallback full resume generation"""
        return f"""
PROFESSIONAL SUMMARY
{enhanced_data.get('enhanced_summary', 'Experienced professional with strong skills and dedication to excellence.')}

CORE COMPETENCIES
{', '.join(enhanced_data.get('enhanced_skills', {}).get('technical', []) + enhanced_data.get('enhanced_skills', {}).get('soft_skills', []))}

PROFESSIONAL EXPERIENCE
{chr(10).join([f"{exp.get('role', 'Role')} - {exp.get('company', 'Company')}" + chr(10) + chr(10).join([f"• {desc}" for desc in exp.get('enhanced_description', ['Performed professional duties'])]) for exp in enhanced_data.get('enhanced_experience', [])])}
"""
