const toISO = (d) => d.toISOString().split('T')[0]

const addDays = (d, n) => {
  const r = new Date(d)
  r.setDate(r.getDate() + n)
  return r
}

export function getCurrentPeriod(user) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  if (user.pay_period_type === 'weekly') {
    // pay_period_value: 0=Mon … 6=Sun
    const todayDay = (today.getDay() + 6) % 7 // JS Sun=0 → Mon=0
    const daysBack = (todayDay - user.pay_period_value + 7) % 7
    const start = addDays(today, -daysBack)
    return { start: toISO(start), end: toISO(addDays(start, 6)) }
  }

  if (user.pay_period_type === 'fortnightly') {
    const anchor = new Date(user.pay_period_anchor + 'T00:00:00')
    const daysSince = Math.floor((today - anchor) / 86400000)
    const offset = ((daysSince % 14) + 14) % 14
    const start = addDays(today, -offset)
    return { start: toISO(start), end: toISO(addDays(start, 13)) }
  }

  if (user.pay_period_type === 'monthly') {
    const sd = user.pay_period_value // 1–28
    let start, end
    if (today.getDate() >= sd) {
      start = new Date(today.getFullYear(), today.getMonth(), sd)
      end = new Date(today.getFullYear(), today.getMonth() + 1, sd - 1)
    } else {
      start = new Date(today.getFullYear(), today.getMonth() - 1, sd)
      end = new Date(today.getFullYear(), today.getMonth(), sd - 1)
    }
    return { start: toISO(start), end: toISO(end) }
  }

  // Fallback: current Mon–Sun week
  const todayDay = (today.getDay() + 6) % 7
  const start = addDays(today, -todayDay)
  return { start: toISO(start), end: toISO(addDays(start, 6)) }
}

export function formatDate(iso) {
  const d = new Date(iso + 'T00:00:00')
  return d.toLocaleDateString('en-AU', { day: 'numeric', month: 'short', year: 'numeric' })
}

export function formatTime(hhmm) {
  const [h, m] = hhmm.split(':').map(Number)
  const suffix = h >= 12 ? 'pm' : 'am'
  const hour = h % 12 || 12
  return `${hour}:${m.toString().padStart(2, '0')}${suffix}`
}

export function todayISO() {
  return toISO(new Date())
}
