# from typing import Optional

# from pydantic import BaseModel, Field, EmailStr


# class ResumeInfo(BaseModel):
#     name: str
#     address: str
#     languages: list[str]
#     college: str
#     degree: str
#     skills: list[str]
#     tools: list[str]
#     certificates: list[str]
#     linkedin_id: str
#     github_id: str
#     twitter_id: str
#     website: str
#     email: EmailStr
#     professional_introduction: str
#     tagline: str


# class ParsedResume(BaseModel):
#     """
#     Container for a single record of parsed-resume
#     """

#     name: str = Field(...)
#     generated_info: ResumeInfo
#     target_info: Optional[ResumeInfo] = None


# class UpdateParsedResumeActualInfo(BaseModel):
#     """
#     Model to update the actual_info of the parsed-resume
#     """

#     target_info: ResumeInfo


# class ParsedResumeCollection(BaseModel):
#     """
#     Model to list all the parsed-resumes
#     """

#     parsed_resumes: list[ParsedResume]
