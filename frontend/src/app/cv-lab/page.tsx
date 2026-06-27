import type { Metadata } from 'next';
import CVLabInteractive from './components/CVLabInteractive';

import Header from '@/components/common/Header';

export const metadata: Metadata = {
  title: 'CV Lab — InterviewNinja',
  description: 'Interactive Computer Vision lab with AI-powered topic exploration, quizzes, and deep-dive sessions.',
};

export default function CVLabPage() {
  return (
    <>
      <Header />
      <CVLabInteractive />
    </>
  );
}
