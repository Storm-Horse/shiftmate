import { NavLink } from 'react-router-dom'
import { PlusCircle, CalendarDays, Settings } from 'lucide-react'

const tabs = [
  { to: '/', icon: PlusCircle, label: 'Log' },
  { to: '/shifts', icon: CalendarDays, label: 'Shifts' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export default function Navbar() {
  return (
    <nav className="fixed bottom-0 inset-x-0 max-w-lg mx-auto bg-white border-t border-slate-200 safe-bottom z-50">
      <div className="flex">
        {tabs.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex-1 flex flex-col items-center justify-center py-3 gap-0.5 text-xs font-medium transition-colors ${
                isActive ? 'text-blue-700' : 'text-slate-400'
              }`
            }
          >
            <Icon size={22} strokeWidth={1.75} />
            {label}
          </NavLink>
        ))}
      </div>
    </nav>
  )
}
