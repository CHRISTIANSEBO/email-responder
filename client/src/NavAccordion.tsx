import { useRef, useState } from 'react';
import { gsap } from 'gsap';
import { GoArrowUpRight } from 'react-icons/go';
import './NavAccordion.css';

type NavLink = { label: string; ariaLabel: string; onClick?: () => void };
type NavSection = { label: string; links: NavLink[] };

interface Props {
  sections: NavSection[];
}

function AccordionItem({ section }: { section: NavSection }) {
  const [open, setOpen] = useState(false);
  const bodyRef = useRef<HTMLDivElement>(null);

  const toggle = () => {
    const el = bodyRef.current;
    if (!el) return;
    if (!open) {
      gsap.fromTo(el,
        { height: 0, opacity: 0 },
        { height: 'auto', opacity: 1, duration: 0.28, ease: 'power3.out' }
      );
    } else {
      gsap.to(el, { height: 0, opacity: 0, duration: 0.22, ease: 'power3.in' });
    }
    setOpen(o => !o);
  };

  return (
    <div className={`accordion-item ${open ? 'open' : ''}`}>
      <button type="button" className="accordion-trigger" onClick={toggle}>
        <span>{section.label}</span>
        <svg className="accordion-chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </button>
      <div ref={bodyRef} className="accordion-body" style={{ height: 0, overflow: 'hidden', opacity: 0 }}>
        {section.links.map((lnk, i) => (
          <button
            key={i}
            type="button"
            className="accordion-link"
            aria-label={lnk.ariaLabel}
            onClick={lnk.onClick}
          >
            <GoArrowUpRight size={13} aria-hidden="true" />
            {lnk.label}
          </button>
        ))}
      </div>
    </div>
  );
}

export default function NavAccordion({ sections }: Props) {
  return (
    <div className="nav-accordion">
      {sections.map((s, i) => <AccordionItem key={i} section={s} />)}
    </div>
  );
}
