import type { Metadata } from 'next';
import SystemDesignLabInteractive from './components/SystemDesignLabInteractive';

import Header from '@/components/common/Header';

export const metadata: Metadata = {
  title: 'System Design Lab — InterviewNinja',
  description: 'Interactive System Design lab with 16 on-demand sections covering requirements, estimation, architecture, scaling, reliability, and more.',
};

export default function SystemDesignLabPage() {
  return (
    <>
      <Header />
      <SystemDesignLabInteractive />
    </>
  );
}
