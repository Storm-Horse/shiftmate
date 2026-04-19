import { useState, useEffect, useCallback } from 'react'
import { ChevronLeft, ChevronRight, Send, Download, CheckCircle2 } from 'lucide-react'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'
import { getCurrentPeriod, formatDate } from '../utils/payPeriod'
import ShiftCard from '../components/ShiftCard'

function addDays(iso, n) {
  const d = new Date(iso + 'T00:00:00')
  d.setDate(d.getDate() + n)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}


function groupByDate(shifts) {
  const map = {}
  shifts.forEach((s) => {
    if (!map[s.date]) map[s.date] = []
    map[s.date].push(s)
  })
  return Object.entries(map).sort(([a], [b]) => a.localeCompare(b))
}

export default function ShiftsPage() {
  const { user } = useAuth()
  const [period, setPeriod] = useState(() => getCurrentPeriod())
  const [shifts, setShifts] = useState([])
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [confirm, setConfirm] = useState(false)
  const [recipientOverride, setRecipientOverride] = useState('')
  const [toast, setToast] = useState(null)

  const loadShifts = useCallback(async () => {
    setLoading(true)
    try {
      const { data } = await api.get('/shifts', {
        params: { start: period.start, end: period.end },
      })
      setShifts(data)
    } finally {
      setLoading(false)
    }
  }, [period])

  useEffect(() => { loadShifts() }, [loadShifts])

  const showToast = (msg, ok = true) => {
    setToast({ msg, ok })
    setTimeout(() => setToast(null), 4000)
  }

  const navigate = (dir) => {
    setPeriod({ start: addDays(period.start, dir * 7), end: addDays(period.end, dir * 7) })
  }

  const deleteShift = async (id) => {
    await api.delete(`/shifts/${id}`)
    setShifts((prev) => prev.filter((s) => s.id !== id))
  }

  const sendTimesheet = async () => {
    setSending(true)
    try {
      const payload = { period_start: period.start, period_end: period.end }
      if (recipientOverride) payload.recipient_email = recipientOverride
      const { data } = await api.post('/timesheets/send', payload)
      showToast(data.message)
      setConfirm(false)
      setRecipientOverride('')
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to send', false)
    } finally {
      setSending(false)
    }
  }

  const downloadUrl = `/api/v1/timesheets/download?period_start=${period.start}&period_end=${period.end}`

  const totalHours = shifts.reduce((sum, s) => sum + s.hours, 0)
  const jobTotals = shifts.reduce((acc, s) => {
    acc[s.job_name] = (acc[s.job_name] || 0) + s.hours
    return acc
  }, {})
  const grouped = groupByDate(shifts)

  return (
    <div className="px-4 pt-5 pb-4">
      {/* Period navigator */}
      <div className="flex items-center gap-2 mb-5">
        <button
          onClick={() => navigate(-1)}
          className="p-2 rounded-xl border border-slate-200 bg-white text-slate-600 active:bg-slate-100"
        >
          <ChevronLeft size={20} />
        </button>
        <div className="flex-1 text-center">
          <div className="text-xs text-slate-500 font-medium uppercase tracking-wide">Pay period</div>
          <div className="font-semibold text-slate-800">
            {formatDate(period.start)} – {formatDate(period.end)}
          </div>
        </div>
        <button
          onClick={() => navigate(1)}
          className="p-2 rounded-xl border border-slate-200 bg-white text-slate-600 active:bg-slate-100"
        >
          <ChevronRight size={20} />
        </button>
      </div>

      {/* Summary card */}
      {shifts.length > 0 && (
        <div className="bg-blue-700 rounded-2xl p-4 mb-5 text-white">
          <div className="flex items-baseline gap-1 mb-3">
            <span className="text-4xl font-bold">{totalHours.toFixed(2)}</span>
            <span className="text-blue-200 font-medium">hrs total</span>
          </div>
          <div className="space-y-1">
            {Object.entries(jobTotals).map(([job, hrs]) => (
              <div key={job} className="flex justify-between text-sm">
                <span className="text-blue-100 truncate mr-4">{job}</span>
                <span className="text-white font-semibold whitespace-nowrap">{hrs.toFixed(2)} hrs</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Shift list */}
      {loading ? (
        <div className="text-center text-slate-400 py-10">Loading…</div>
      ) : shifts.length === 0 ? (
        <div className="text-center text-slate-400 py-10">
          <p>No shifts logged for this period.</p>
          <p className="text-sm mt-1">Go to Log to add shifts.</p>
        </div>
      ) : (
        <div className="space-y-4 mb-6">
          {grouped.map(([date, dayShifts]) => (
            <div key={date}>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1.5">
                {formatDate(date)}
              </p>
              <div className="space-y-2">
                {dayShifts.map((s) => (
                  <ShiftCard key={s.id} shift={s} onDelete={deleteShift} />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Actions */}
      {shifts.length > 0 && !confirm && (
        <div className="flex gap-3">
          <button
            onClick={() => setConfirm(true)}
            className="flex-1 flex items-center justify-center gap-2 bg-blue-700 text-white font-semibold rounded-xl py-4 hover:bg-blue-800 active:bg-blue-900 transition-colors"
          >
            <Send size={18} />
            Send timesheet
          </button>
          <a
            href={downloadUrl}
            download
            className="flex items-center justify-center gap-2 border border-slate-300 bg-white text-slate-700 font-semibold rounded-xl px-4 py-4 hover:bg-slate-50 active:bg-slate-100 transition-colors"
          >
            <Download size={18} />
          </a>
        </div>
      )}

      {/* Confirm send panel */}
      {confirm && (
        <div className="bg-white rounded-2xl border border-slate-200 p-4 space-y-3">
          <p className="font-semibold text-slate-800">Send timesheet</p>
          <p className="text-sm text-slate-500">
            Recipient: <strong>{user.recipient_email || '(not set)'}</strong>
          </p>
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">
              Override recipient <span className="font-normal">(optional)</span>
            </label>
            <input
              type="email"
              value={recipientOverride}
              onChange={(e) => setRecipientOverride(e.target.value)}
              placeholder={user.recipient_email || 'email@example.com'}
              className="w-full border border-slate-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => { setConfirm(false); setRecipientOverride('') }}
              className="flex-1 border border-slate-300 text-slate-700 font-semibold rounded-xl py-3 hover:bg-slate-50 active:bg-slate-100 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={sendTimesheet}
              disabled={sending}
              className="flex-1 bg-blue-700 text-white font-semibold rounded-xl py-3 hover:bg-blue-800 active:bg-blue-900 disabled:opacity-50 transition-colors"
            >
              {sending ? 'Sending…' : 'Confirm send'}
            </button>
          </div>
        </div>
      )}

      {/* Toast */}
      {toast && (
        <div
          className={`fixed bottom-24 inset-x-4 max-w-sm mx-auto flex items-center gap-2 px-4 py-3 rounded-xl shadow-lg text-white text-sm font-medium z-50 ${
            toast.ok ? 'bg-green-600' : 'bg-red-600'
          }`}
        >
          {toast.ok && <CheckCircle2 size={16} />}
          {toast.msg}
        </div>
      )}
    </div>
  )
}
