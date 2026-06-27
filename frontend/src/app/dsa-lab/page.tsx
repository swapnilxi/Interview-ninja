import type { Metadata } from 'next';
import DSALabInteractive from './components/DSALabInteractive';
import Header from '@/components/common/Header';

export const metadata: Metadata = {
  title: 'DSA Lab — InterviewNinja',
  description: 'Interactive Data Structures and Algorithms lab with AI-powered topic exploration, quizzes, and deep-dive sessions.',
};

export default function DSALabPage() {
  return (
    <>
      <Header />
      <DSALabInteractive />
    </>
  );
}
