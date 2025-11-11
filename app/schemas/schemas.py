from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Generic, TypeVar, Any, Dict
from datetime import datetime, date
from enum import Enum

# Import enums directly from models file
from app.models.models import UserRole, State, ElectionType

T = TypeVar('T')

class StandardResponse(BaseModel, Generic[T]):
    status: bool
    data: Optional[T] = None
    error: Optional[str] = None
    message: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

# Political Party Schemas
class PoliticalPartyBase(BaseModel):
    name: str
    acronym: str
    logo_url: Optional[str] = None
    description: Optional[str] = None
    founded_date: Optional[datetime] = None

class PoliticalPartyCreate(PoliticalPartyBase):
    pass

class PoliticalPartyResponse(PoliticalPartyBase):
    id: int
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }

# User Schemas
class UserBase(BaseModel):
    nin: str
    email: EmailStr
    full_name: str
    state_of_residence: State
    profile_image_url: Optional[str] = None
    date_of_birth: Optional[date] = None
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    password: str

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

    @validator('nin')
    def nin_length(cls, v):
        if len(v) != 11:
            raise ValueError('NIN must be 11 digits long')
        if not v.isdigit():
            raise ValueError('NIN must contain only digits')
        return v

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    registration_date: datetime
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

# OTP Schemas
class OTPVerificationRequest(BaseModel):
    email: EmailStr
    otp_code: str

class OTPResponse(BaseModel):
    message: str
    email: EmailStr

# Password Reset Schemas
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @validator('new_password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

# Election Schemas
class ElectionBase(BaseModel):
    title: str
    description: Optional[str] = None
    election_type: ElectionType
    state: Optional[State] = None
    is_active: bool = False
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ElectionCreate(ElectionBase):
    pass

class ElectionResponse(ElectionBase):
    id: int
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }

class PositionBase(BaseModel):
    title: str
    description: Optional[str] = None

class PositionCreate(PositionBase):
    election_id: int

class PositionResponse(PositionBase):
    id: int
    election_id: int
    
    model_config = {
        "from_attributes": True
    }

class CandidateBase(BaseModel):
    name: str
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None

class CandidateCreate(CandidateBase):
    position_id: int
    party_id: Optional[int] = None

class CandidateResponse(CandidateBase):
    id: int
    position_id: int
    party: Optional[PoliticalPartyResponse] = None
    
    model_config = {
        "from_attributes": True
    }

class VoteRequest(BaseModel):
    candidate_id: int

class VoteResponse(BaseModel):
    vote_id: int
    message: str
    
    model_config = {
        "from_attributes": True
    }

# Extended schemas for detailed views
class CandidateWithVotes(CandidateResponse):
    votes_count: int = 0

class PositionWithCandidates(PositionResponse):
    candidates: List[CandidateWithVotes] = []

class ElectionWithPositions(ElectionResponse):
    positions: List[PositionWithCandidates] = []
    total_votes: int = 0

class VoterProfile(BaseModel):
    user: UserResponse
    total_votes_cast: int
    elections_participated: List[str]
    
    model_config = {
        "from_attributes": True
    }

# Election results with party information
class PartyResults(BaseModel):
    party: PoliticalPartyResponse
    total_votes: int
    percentage: float
    candidates: List[CandidateWithVotes]

class ElectionResultsDetailed(BaseModel):
    election: ElectionResponse
    party_results: List[PartyResults]
    total_votes: int
    voter_turnout: float
    
    model_config = {
        "from_attributes": True
    }