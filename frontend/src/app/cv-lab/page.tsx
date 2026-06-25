import type { Metadata } from 'next';
import CVLabInteractive from './components/CVLabInteractive';

export const metadata: Metadata = {
  title: 'CV Lab — InterviewNinja',
  description: 'Interactive Computer Vision lab with AI-powered topic exploration, quizzes, and deep-dive sessions.',
};

export default function CVLabPage() {
  return <CVLabInteractive />;
}
