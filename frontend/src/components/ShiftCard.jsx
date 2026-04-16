import { Trash2 } from 'lucide-react'
import { formatTime } from '../utils/payPeriod'

export default function ShiftCard({ shift, onDelete }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 px-4 py-3 flex items-center gap-3">
      <div className="flex-1 min-w-0">
        <div className="flex items-baseline gap-2">
          <span className="font-semibold text-slate-800 truncate">{shift.job_name}</span>
          <span className="text-blue-700 font-bold text-sm whitespace-nowrap">{shift.hours}h</span>
        </div>
        <div className="text-sm text-slate-500 mt-0.5">
          {shift.start_time
            ? `${formatTime(shift.start_time)} – ${formatTime(shift.end_time)}`
            : `${shift.hours} hrs logged`}
          {shift.start_time && shift.break_minutes > 0 && (
            <span className="ml-2 text-slate-400">({shift.break_minutes}m break)</span>
          )}
        </div>
        {shift.notes && (
          <div className="text-xs text-slate-400 mt-0.5 truncate">{shift.notes}</div>
        )}
      </div>
      {onDelete && (
        <button
          onClick={() => onDelete(shift.id)}
          className="p-2 text-slate-300 hover:text-red-500 active:text-red-600 transition-colors rounded-lg"
          aria-label="Delete shift"
        >
          <Trash2 size={18} />
        </button>
      )}
    </div>
  )
}
