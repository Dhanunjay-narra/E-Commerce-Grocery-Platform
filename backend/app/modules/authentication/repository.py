"""Authentication database repository layer."""
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.authentication.models import UserSession, RefreshToken, OTPRecord, LoginHistory
from app.modules.users.models import User, UserProfile
from app.core.config import settings


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(and_(User.email == email.lower(), User.is_deleted == False))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_phone(self, phone: str) -> Optional[User]:
        query = select(User).where(and_(User.phone == phone, User.is_deleted == False))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_identifier(self, identifier: str) -> Optional[User]:
        if "@" in identifier:
            return await self.get_user_by_email(identifier)
        return await self.get_user_by_phone(identifier)

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        query = select(User).where(and_(User.id == user_id, User.is_deleted == False))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        email: str,
        hashed_password: Optional[str],
        full_name: str,
        phone: Optional[str] = None,
        role: str = "CUSTOMER",
        is_verified: bool = False,
        phone_verified: bool = False,
    ) -> User:
        user = User(
            email=email.lower(),
            hashed_password=hashed_password,
            full_name=full_name,
            phone=phone,
            role=role,
            is_verified=is_verified,
            phone_verified=phone_verified,
        )
        self.db.add(user)
        await self.db.flush()

        profile = UserProfile(user_id=user.id)
        self.db.add(profile)
        await self.db.flush()
        return user

    async def create_session(
        self,
        user_id: str,
        session_token_jti: str,
        expires_at: datetime,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> UserSession:
        session = UserSession(
            user_id=user_id,
            session_token_jti=session_token_jti,
            expires_at=expires_at,
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(session)
        await self.db.flush()
        return session

    async def get_session_by_jti(self, jti: str) -> Optional[UserSession]:
        query = select(UserSession).where(
            and_(
                UserSession.session_token_jti == jti,
                UserSession.is_revoked == False,
                UserSession.expires_at > datetime.now(timezone.utc),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def revoke_session(self, jti: str) -> None:
        stmt = update(UserSession).where(UserSession.session_token_jti == jti).values(is_revoked=True)
        await self.db.execute(stmt)

    async def revoke_all_user_sessions(self, user_id: str) -> None:
        stmt = update(UserSession).where(UserSession.user_id == user_id).values(is_revoked=True)
        await self.db.execute(stmt)
        stmt_refresh = update(RefreshToken).where(RefreshToken.user_id == user_id).values(is_revoked=True)
        await self.db.execute(stmt_refresh)

    async def get_user_sessions(self, user_id: str) -> List[UserSession]:
        query = select(UserSession).where(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_revoked == False,
                UserSession.expires_at > datetime.now(timezone.utc),
            )
        ).order_by(UserSession.last_active_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_refresh_token(
        self,
        user_id: str,
        token_jti: str,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        token = RefreshToken(
            user_id=user_id,
            token_jti=token_jti,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.db.add(token)
        await self.db.flush()
        return token

    async def get_refresh_token(self, token_jti: str) -> Optional[RefreshToken]:
        query = select(RefreshToken).where(
            and_(
                RefreshToken.token_jti == token_jti,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.now(timezone.utc),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, token_jti: str) -> None:
        stmt = update(RefreshToken).where(RefreshToken.token_jti == token_jti).values(is_revoked=True)
        await self.db.execute(stmt)

    async def create_otp(
        self,
        identifier: str,
        otp_code: str,
        purpose: str,
        expires_at: datetime,
    ) -> OTPRecord:
        otp = OTPRecord(
            identifier=identifier.lower().strip(),
            otp_code=otp_code,
            purpose=purpose,
            expires_at=expires_at,
        )
        self.db.add(otp)
        await self.db.flush()
        return otp

    async def get_valid_otp(self, identifier: str, purpose: str) -> Optional[OTPRecord]:
        query = select(OTPRecord).where(
            and_(
                OTPRecord.identifier == identifier.lower().strip(),
                OTPRecord.purpose == purpose,
                OTPRecord.is_used == False,
                OTPRecord.expires_at > datetime.now(timezone.utc),
            )
        ).order_by(OTPRecord.created_at.desc())
        result = await self.db.execute(query)
        return result.scalars().first()

    async def record_login_attempt(
        self,
        identifier: str,
        success: bool,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        failure_reason: Optional[str] = None,
    ) -> None:
        history = LoginHistory(
            user_id=user_id,
            identifier=identifier,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason,
        )
        self.db.add(history)
        await self.db.flush()

    async def handle_failed_login(self, user: User) -> None:
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            user.lockout_until = datetime.now(timezone.utc) + timedelta(minutes=settings.LOCKOUT_DURATION_MINUTES)
        await self.db.flush()

    async def reset_failed_login(self, user: User) -> None:
        user.failed_login_attempts = 0
        user.lockout_until = None
        await self.db.flush()
