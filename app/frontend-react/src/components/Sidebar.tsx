import type { Fixture } from "../lib/types";
import { History } from "./History";
import { TeamSearch } from "./TeamSearch";

interface SidebarProps {
  selectedFixture: Fixture | null;
  onSelectFixture: (fixture: Fixture) => void;
  historyRefreshToken: number;
}

export function Sidebar({ selectedFixture, onSelectFixture, historyRefreshToken }: SidebarProps) {
  return (
    <aside className="sidebar" aria-label="Panel lateral">
      <TeamSearch selectedFixture={selectedFixture} onSelectFixture={onSelectFixture} />
      <History refreshToken={historyRefreshToken} />
    </aside>
  );
}
