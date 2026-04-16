import { useState, useEffect, useCallback } from 'react'
import { CheckCircle2, Clock } from 'lucide-react'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'
import { todayISO, formatDate } from '../utils/payPeriod'
import ShiftCard from '../components/ShiftCard'

const todayStr = todayISO()

function defaultForm() {
  return {
    date: todayStr,
    mode: 'times',   // 'times' | 'hours'
    start_time: '',
    end_time: '',
    direct_hours: '',
    break_minutes: 0,
    job_name: '',
    notes: '',
  }
}

export default function HomePage() {
  const { user } = useAuth()
  const [form, setForm] = useState(defaultForm())
  const [shifts, setShifts] = useState([])
  const [jobSuggestions, setJobSuggestions] = useState([])
  const [saving, setSaving] = useState(false)
  const [toast, setToast] = useState(null)

  const loadShifts = useCallback(async () => {
    const { data } = await api.get('/shifts', { params: { start: form.date, end: form.date } })
    setShifts(data)
  }, [form.date])

  useEffect(() => { loadShifts() }, [loadShifts])

  useEffect(() => {
    api.get('/shifts/jobs').then(({ data }) => setJobSuggestions(data))
  }, [])

  const showToast = (msg, ok = true) => {
    setToast({ msg, ok })
    setTimeout(() => setToast(null), 3000)
  }

  const submit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      const payload = {
        date: form.date,
        job_name: form.job_name,
        break_minutes: Number(form.break_minutes) || 0,
        notes: form.notes || null,
      }
      if (form.mode === 'times') {
        payload.start_time = form.start_time
        payload.end_time = form.end_time
      } else {
        payload.direct_hours = parseFloat(form.direct_hours)
      }

      await api.post('/shifts', payload)
      setForm((f) => ({ ...defaultForm(), date: f.date, mode: f.mode, job_name: f.job_name }))
      await loadShifts()
      const { data } = await api.get('/shifts/jobs')
      setJobSuggestions(data)
      showToast('Shift logged')
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to save', false)
    } finally {
      setSaving(false)
    }
  }

  const deleteShift = async (id) => {
    await api.delete(`/shifts/${id}`)
    setShifts((prev) => prev.filter((s) => s.id !== id))
  }

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  const isValid = form.mode === 'times'
    ? form.start_time && form.end_time && form.job_name
    : form.direct_hours && form.job_name

  return (
    <div className="px-4 pt-5 pb-4">
      {/* Header */}
      <div className="mb-5">
        <p className="text-sm text-slate-500 font-medium">{formatDate(form.date)}</p>
        <h1 className="text-2xl font-bold text-slate-900">
          Hey, {user.name.split(' ')[0]}
        </h1>
      </div>

      {/* Log shift form */}
      <form onSubmit={submit} className="bg-white rounded-2xl border border-slate-200 p-4 space-y-3 mb-6">
        <div className="flex items-center gap-2 mb-1">
          <Clock size={16} className="text-blue-700" />
          <span className="font-semibold text-slate-800">Log a shift</span>
        </div>

        {/* Date */}
        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">Date</label>
          <input
            type="date"
            value={form.date}
            onChange={(e) => set('date', e.target.value)}
            className="w-full border border-slate-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Job name */}
        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">Job name</label>
          <input
            list="job-suggestions"
            type="text"
            required
            value={form.job_name}
            onChange={(e) => set('job_name', e.target.value)}
            placeholder="e.g. Warehouse, Café"
            className="w-full border border-slate-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <datalist id="job-suggestions">
            {jobSuggestions.map((j) => <option key={j} value={j} />)}
          </datalist>
        </div>

        {/* Mode toggle */}
        <div className="flex rounded-xl border border-slate-200 overflow-hidden">
          <button
            type="button"
            onClick={() => set('mode', 'times')}
            className={`flex-1 py-2.5 text-sm font-medium transition-colors ${
              form.mode === 'times'
                ? 'bg-blue-700 text-white'
                : 'bg-white text-slate-500 hover:bg-slate-50'
            }`}
          >
            Start &amp; end time
          </button>
          <button
            type="button"
            onClick={() => set('mode', 'hours')}
            className={`flex-1 py-2.5 text-sm font-medium transition-colors ${
              form.mode === 'hours'
                ? 'bg-blue-700 text-white'
                : 'bg-white text-slate-500 hover:bg-slate-50'
            }`}
          >
            Total hours
          </button>
        </div>

        {/* Time inputs */}
        {form.mode === 'times' && (
          <>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Start time</label>
                <input
                  type="time"
                  required
                  value={form.start_time}
                  onChange={(e) => set('start_time', e.target.value)}
                  className="w-full border border-slate-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">End time</label>
                <input
                  type="time"
                  required
                  value={form.end_time}
                  onChange={(e) => set('end_time', e.target.value)}
                  className="w-full border border-slate-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">
                Break <span className="font-normal text-slate-400">(minutes, optional)</span>
              </label>
              <input
                type="number"
                min="0"
                step="5"
                value={form.break_minutes || ''}
                onChange={(e) => set('break_minutes', e.target.value)}
                placeholder="0"
                className="w-full border border-slate-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </>
        )}

        {/* Direct hours input */}
        {form.mode === 'hours' && (
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">Hours worked</label>
            <input
              type="number"
              required
              min="0"
              max="24"
              step="any"
              value={form.direct_hours}
              onChange={(e) => set('direct_hours', e.target.value)}
              placeholder="e.g. 7.5"
              className="w-full border border-slate-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg"
            />
          </div>
        )}

        {/* Notes */}
        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">
            Notes <span className="font-normal text-slate-400">(optional)</span>
          </label>
          <input
            type="text"
            value={form.notes}
            onChange={(e) => set('notes', e.target.value)}
            placeholder="Overtime, public holiday…"
            className="w-full border border-slate-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          type="submit"
          disabled={saving || !isValid}
          className="w-full bg-blue-700 text-white font-semibold rounded-xl py-4 text-base hover:bg-blue-800 active:bg-blue-900 disabled:opacity-50 transition-colors mt-1"
        >
          {saving ? 'Saving…' : 'Log shift'}
        </button>
      </form>

      {/* Today's shifts */}
      {shifts.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-2">
            {form.date === todayStr ? "Today's shifts" : `Shifts on ${formatDate(form.date)}`}
          </h2>
          <div className="space-y-2">
            {shifts.map((s) => (
              <ShiftCard key={s.id} shift={s} onDelete={deleteShift} />
            ))}
          </div>
        </div>
      )}

      {/* Toast */}
      {toast && (
        <div
          className={`fixed bottom-24 inset-x-4 max-w-sm mx-auto flex items-center gap-2 px-4 py-3 rounded-xl shadow-lg text-white text-sm font-medium z-50 transition-all ${
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
