"""
Cover Letter Generator Service
Uses Google Gemini API (Free tier) to generate personalized cover letters
"""

import google.generativeai as genai
import os
import logging
import time
from typing import Dict, Any, Optional
import json

class CoverLetterGenerator:
    """Generate cover letters using Google Gemini API (Free)"""

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
                raise ValueError("GEMINI_API_KEY not found")

            # Configure Gemini
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')

            # Rate limiting for free tier
            self.rate_limit_delay = 2
            self.last_request_time = 0

            self.logger.info("✅ Gemini API configured for cover letter generation")

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

    def generate(self, resume_content: str, user_preferences: Dict[str, Any], 
                job_description: str = "", company_name: str = "") -> Dict[str, str]:
        """Generate personalized cover letter"""

        if not self.model:
            return self._fallback_cover_letter(user_preferences, company_name)

        try:
            # Generate multiple cover letter styles
            cover_letters = {}

            # Professional style
            cover_letters['professional'] = self._generate_professional_cover_letter(
                resume_content, user_preferences, job_description, company_name
            )

            # Creative style  
            cover_letters['creative'] = self._generate_creative_cover_letter(
                resume_content, user_preferences, job_description, company_name
            )

            # Technical style
            cover_letters['technical'] = self._generate_technical_cover_letter(
                resume_content, user_preferences, job_description, company_name
            )

            # Entry-level style
            cover_letters['entry_level'] = self._generate_entry_level_cover_letter(
                resume_content, user_preferences, job_description, company_name
            )

            return cover_letters

        except Exception as e:
            self.logger.error(f"Cover letter generation failed: {e}")
            return self._fallback_cover_letter(user_preferences, company_name)

    def _generate_professional_cover_letter(self, resume_content: str, 
                                          user_preferences: Dict, job_description: str, 
                                          company_name: str) -> str:
        """Generate professional style cover letter"""
        try:
            self._rate_limit()

            prompt = f"""
            You are a professional career coach. Write a compelling cover letter using this information:

            Resume Summary: {resume_content[:1500]}
            Desired Role: {user_preferences.get('desired_role', 'Professional Position')}
            Experience Level: {user_preferences.get('experience_level', 'Mid-Level')}
            Company: {company_name or 'the organization'}
            Job Description: {job_description[:800] if job_description else 'Not provided'}
            Work Arrangement: {user_preferences.get('work_arrangement', 'Any')}
            Location: {user_preferences.get('location', 'Flexible')}

            Write a professional cover letter that:
            1. Opens with a strong hook that mentions the specific role
            2. Highlights relevant experience and achievements
            3. Shows knowledge of the company (if company name provided)
            4. Demonstrates value proposition
            5. Includes a professional closing
            6. Is 3-4 paragraphs, approximately 250-300 words
            7. Uses professional tone throughout
            8. Includes specific examples from the resume

            Format as a complete cover letter with proper salutation and closing.
            Return only the cover letter content, no additional text.
            """

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            self.logger.error(f"Professional cover letter generation failed: {e}")
            return self._fallback_professional_cover_letter(user_preferences, company_name)

    def _generate_creative_cover_letter(self, resume_content: str, 
                                      user_preferences: Dict, job_description: str, 
                                      company_name: str) -> str:
        """Generate creative style cover letter"""
        try:
            self._rate_limit()

            prompt = f"""
            You are a creative writing expert. Write an engaging, creative cover letter using this information:

            Resume Summary: {resume_content[:1500]}
            Desired Role: {user_preferences.get('desired_role', 'Creative Position')}
            Experience Level: {user_preferences.get('experience_level', 'Mid-Level')}
            Company: {company_name or 'the organization'}

            Write a creative cover letter that:
            1. Opens with an engaging story or unique angle
            2. Shows personality while maintaining professionalism
            3. Uses creative language and metaphors
            4. Demonstrates passion and enthusiasm
            5. Still includes relevant qualifications
            6. Has a memorable closing
            7. Is 3-4 paragraphs, approximately 250-300 words
            8. Balances creativity with professional requirements

            Format as a complete cover letter.
            Return only the cover letter content, no additional text.
            """

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            self.logger.error(f"Creative cover letter generation failed: {e}")
            return self._fallback_creative_cover_letter(user_preferences, company_name)

    def _generate_technical_cover_letter(self, resume_content: str, 
                                       user_preferences: Dict, job_description: str, 
                                       company_name: str) -> str:
        """Generate technical style cover letter"""
        try:
            self._rate_limit()

            prompt = f"""
            You are a technical recruiter. Write a technical cover letter using this information:

            Resume Summary: {resume_content[:1500]}
            Desired Role: {user_preferences.get('desired_role', 'Technical Position')}
            Experience Level: {user_preferences.get('experience_level', 'Mid-Level')}
            Company: {company_name or 'the organization'}
            Job Description: {job_description[:800] if job_description else 'Not provided'}

            Write a technical cover letter that:
            1. Focuses on technical skills and achievements
            2. Includes specific technologies and methodologies
            3. Mentions relevant projects and outcomes
            4. Shows problem-solving capabilities
            5. Demonstrates technical depth
            6. Uses industry-appropriate terminology
            7. Is 3-4 paragraphs, approximately 250-300 words
            8. Balances technical details with business impact

            Format as a complete cover letter.
            Return only the cover letter content, no additional text.
            """

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            self.logger.error(f"Technical cover letter generation failed: {e}")
            return self._fallback_technical_cover_letter(user_preferences, company_name)

    def _generate_entry_level_cover_letter(self, resume_content: str, 
                                         user_preferences: Dict, job_description: str, 
                                         company_name: str) -> str:
        """Generate entry-level style cover letter"""
        try:
            self._rate_limit()

            prompt = f"""
            You are a career counselor for new graduates. Write an entry-level cover letter using this information:

            Resume Summary: {resume_content[:1500]}
            Desired Role: {user_preferences.get('desired_role', 'Entry Level Position')}
            Company: {company_name or 'the organization'}

            Write an entry-level cover letter that:
            1. Emphasizes potential and enthusiasm over extensive experience
            2. Highlights relevant education, internships, and projects
            3. Shows eagerness to learn and grow
            4. Demonstrates relevant skills and knowledge
            5. Expresses genuine interest in the company/role
            6. Focuses on transferable skills
            7. Is 3-4 paragraphs, approximately 250-300 words
            8. Maintains confident yet humble tone

            Format as a complete cover letter.
            Return only the cover letter content, no additional text.
            """

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            self.logger.error(f"Entry-level cover letter generation failed: {e}")
            return self._fallback_entry_level_cover_letter(user_preferences, company_name)

    def _fallback_cover_letter(self, user_preferences: Dict, company_name: str) -> Dict[str, str]:
        """Fallback cover letters when AI is unavailable"""
        return {
            'professional': self._fallback_professional_cover_letter(user_preferences, company_name),
            'creative': self._fallback_creative_cover_letter(user_preferences, company_name),
            'technical': self._fallback_technical_cover_letter(user_preferences, company_name),
            'entry_level': self._fallback_entry_level_cover_letter(user_preferences, company_name)
        }

    def _fallback_professional_cover_letter(self, user_preferences: Dict, company_name: str) -> str:
        """Fallback professional cover letter"""
        role = user_preferences.get('desired_role', 'this position')
        company = company_name or 'your organization'

        return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {role} position at {company}. With my background in {user_preferences.get('experience_level', 'professional')} experience, I am confident that I would be a valuable addition to your team.

Throughout my career, I have developed strong analytical and problem-solving skills that align well with the requirements of this role. My experience has taught me the importance of attention to detail, effective communication, and collaborative teamwork. I am particularly drawn to {company} because of its reputation for innovation and excellence in the industry.

I am excited about the opportunity to contribute to your team's success and would welcome the chance to discuss how my skills and enthusiasm can benefit {company}. I am available for {user_preferences.get('work_arrangement', 'any')} work arrangements and can start on {user_preferences.get('start_date', 'the agreed upon date')}.

Thank you for considering my application. I look forward to hearing from you soon.

Sincerely,
[Your Name]"""

    def _fallback_creative_cover_letter(self, user_preferences: Dict, company_name: str) -> str:
        """Fallback creative cover letter"""
        role = user_preferences.get('desired_role', 'this exciting position')
        company = company_name or 'your innovative organization'

        return f"""Dear Creative Team,

Picture this: a passionate professional who doesn't just meet expectations but consistently exceeds them. That's the energy I bring to every project, and it's exactly what I'd love to contribute to the {role} at {company}.

My journey has been anything but conventional. Each experience has shaped my unique perspective and strengthened my ability to think outside the box. Whether working on complex projects or collaborating with diverse teams, I've learned that the best solutions often come from the most unexpected places. This creative problem-solving approach is what I'm most excited to bring to {company}.

What truly excites me about this opportunity is the chance to blend my {user_preferences.get('experience_level', 'growing')} expertise with {company}'s innovative culture. I believe that great work happens when passion meets purpose, and I see tremendous potential for both in this role.

I'd love the opportunity to share more about how my unique perspective and enthusiasm can contribute to your team's continued success.

Best regards,
[Your Name]"""

    def _fallback_technical_cover_letter(self, user_preferences: Dict, company_name: str) -> str:
        """Fallback technical cover letter"""
        role = user_preferences.get('desired_role', 'this technical position')
        company = company_name or 'your organization'

        return f"""Dear Technical Hiring Manager,

I am writing to apply for the {role} at {company}. As a {user_preferences.get('experience_level', 'experienced')} professional with a strong technical background, I am excited about the opportunity to contribute to your development team.

My technical expertise spans multiple programming languages, frameworks, and methodologies. I have successfully delivered projects that required both front-end and back-end development, database optimization, and system architecture design. My approach to problem-solving involves thorough analysis, efficient coding practices, and comprehensive testing to ensure robust and scalable solutions.

What sets me apart is my ability to translate complex technical requirements into practical solutions while maintaining clean, well-documented code. I am committed to continuous learning and staying current with emerging technologies and industry best practices. I believe this aligns well with {company}'s commitment to technical excellence.

I would welcome the opportunity to discuss how my technical skills and passion for innovation can contribute to your team's success.

Best regards,
[Your Name]"""

    def _fallback_entry_level_cover_letter(self, user_preferences: Dict, company_name: str) -> str:
        """Fallback entry-level cover letter"""
        role = user_preferences.get('desired_role', 'this entry-level position')
        company = company_name or 'your organization'

        return f"""Dear Hiring Manager,

I am excited to apply for the {role} at {company}. As a recent graduate with a passion for learning and growth, I am eager to begin my professional journey with an organization known for its commitment to excellence.

During my academic career and internship experiences, I have developed a strong foundation in relevant skills and demonstrated my ability to quickly adapt to new challenges. While I may be early in my career, I bring fresh perspectives, enthusiasm, and a strong work ethic. I am particularly drawn to {company} because of its reputation for supporting professional development and fostering innovation.

I am confident that my educational background, combined with my eagerness to learn and contribute, makes me a strong candidate for this role. I am available for {user_preferences.get('work_arrangement', 'any')} work arrangements and am excited about the possibility of {user_preferences.get('relocate', False) and 'relocating if necessary or' or ''} joining your team.

Thank you for considering my application. I look forward to the opportunity to discuss how I can contribute to {company}'s continued success.

Sincerely,
[Your Name]"""
