import * as React from 'react';
import { Avatar } from './Avatar';
import { IconButton } from './IconButton';
import { AIOrb } from './AIOrb';

export interface BottomBarProps extends React.HTMLAttributes<HTMLDivElement> {
  petName: string;
  petAvatarSrc?: string;
  onSwitchPet?: () => void;
  onAdd?: () => void;
  onAI?: () => void;
  showAI?: boolean;
}

export function BottomBar({
  petName,
  petAvatarSrc,
  onSwitchPet,
  onAdd,
  onAI,
  showAI = true,
  className = '',
  ...rest
}: BottomBarProps) {
  return (
    <div className={`kuki-bottombar ${className}`} {...rest}>
      <button type="button" className="kuki-pet-switcher" onClick={onSwitchPet}>
        <Avatar size="sm" src={petAvatarSrc} />
        <span>{petName}</span>
        <svg width="16" height="16" viewBox="0 -960 960 960" fill="currentColor" aria-hidden>
          <path d="M480-344 240-584l56-56 184 184 184-184 56 56-240 240Z" />
        </svg>
      </button>
      <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
        <IconButton appearance="emphasis" size="lg" label="Add entry" onClick={onAdd}>
          <svg width="24" height="24" viewBox="0 -960 960 960" fill="currentColor" aria-hidden>
            <path d="M440-440H200v-80h240v-240h80v240h240v80H520v240h-80v-240Z" />
          </svg>
        </IconButton>
        {showAI && <AIOrb onClick={onAI} />}
      </div>
    </div>
  );
}
