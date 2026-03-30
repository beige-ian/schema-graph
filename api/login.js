import crypto from 'crypto';

function generateToken() {
  const timestamp = Date.now().toString();
  const secret = process.env.AUTH_SECRET || '';
  const hmac = crypto.createHmac('sha256', secret).update('auth:' + timestamp).digest('hex');
  return `${timestamp}.${hmac}`;
}

export default function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).end();
  }

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch { body = {}; }
  }

  const { id, password } = body || {};
  const validId = process.env.AUTH_ID || '';
  const validPw = process.env.AUTH_PASSWORD || '';

  if (!validId || !validPw) {
    return res.status(500).json({ ok: false, error: '서버 설정 오류' });
  }

  const idBuf = Buffer.from(id || '');
  const validIdBuf = Buffer.from(validId);
  const pwBuf = Buffer.from(password || '');
  const validPwBuf = Buffer.from(validPw);

  const idMatch = idBuf.length === validIdBuf.length && crypto.timingSafeEqual(idBuf, validIdBuf);
  const pwMatch = pwBuf.length === validPwBuf.length && crypto.timingSafeEqual(pwBuf, validPwBuf);

  if (idMatch && pwMatch) {
    const token = generateToken();
    return res.status(200).json({ ok: true, token });
  }

  return res.status(401).json({ ok: false, error: 'ID 또는 비밀번호가 올바르지 않습니다.' });
}
