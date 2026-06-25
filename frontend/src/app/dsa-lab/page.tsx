import type { Metadata } from 'next';
import DSALabInteractive from './components/DSALabInteractive';

export const metadata: Metadata = {
  title: 'DSA Lab — InterviewNinja',
  description: 'Interactive Data Structures & Algorithms lab with LeetCode problems, on-demand solutions, and AI-powered guidance.',
};

export default function DSALabPage() {
  return <DSALabInteractive />;
}
