import { useState } from 'react'
import { CheckCircle2, LogOut } from 'lucide-react'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'

export default function SettingsPage() {
  const { user, updateUser, logout } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    name: user.name,
    employer: user.employer || '',
    recipient_email: user.recipient_email || '',
  })
  const [saving, setSaving] = useState(false)
  const [toast, setToast] = useState(null)

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  const showToast = (msg, ok = true) => {
    setToast({ msg, ok })
    setTimeout(() => setToast(null), 3000)
  }

  const save = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      const payload = {
        name: form.name,
        employer: form.employer || null,
        recipient_email: form.recipient_email || null,
        pay_period_type: 'weekly',
        pay_period_value: 0,
        pay_period_anchor: null,
      }
      const { data } = await api.patch('/users/me', payload)
      updateUser(data)
      showToast('Settings saved')
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to save', false)
    } finally {
      setSaving(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="px-4 pt-5 pb-4">
      <h1 className="text-2xl font-bold text-slate-900 mb-5">Settings</h1>

      <form onSubmit={save} className="space-y-5">
        <div className="bg-white rounded-2xl border border-slate-200 p-4 space-y-3">
          <h2 className="font-semibold text-slate-700 text-sm uppercase tracking-wide">Profile</h2>

          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">Your name</label>
            <input
              type="text"
              required
              value={form.name}
              onChange={(e) => set('name', e.target.value)}
              className="w-full border border-slate-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">Employer / company name</label>
            <input
              type="text"
              value={form.employer}
              onChange={(e) => set('employer', e.target.value)}
              placeholder="e.g. Adelaide Custom Electrical"
              className="w-full border border-slate-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-slate-400 mt-1">Appears in the timesheet header.</p>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">Login email</label>
            <input
              type="email"
              disabled
              value={user.email}
              className="w-full border border-slate-200 bg-slate-50 rounded-xl px-4 py-3 text-slate-400 cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">
              Timesheet recipient email
            </label>
            <input
              type="email"
              value={form.recipient_email}
              onChange={(e) => set('recipient_email', e.target.value)}
              placeholder="boss@company.com"
              className="w-full border border-slate-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-slate-400 mt-1">
              Where your timesheet will be emailed when you tap "Send".
            </p>
          </div>
        </div>

        <button
          type="submit"
          disabled={saving}
          className="w-full bg-blue-700 text-white font-semibold rounded-xl py-4 hover:bg-blue-800 active:bg-blue-900 disabled:opacity-50 transition-colors"
        >
          {saving ? 'Saving…' : 'Save settings'}
        </button>
      </form>

      <button
        onClick={handleLogout}
        className="w-full mt-4 flex items-center justify-center gap-2 border border-slate-300 text-slate-600 font-semibold rounded-xl py-3.5 hover:bg-slate-50 active:bg-slate-100 transition-colors"
      >
        <LogOut size={18} />
        Sign out
      </button>

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
