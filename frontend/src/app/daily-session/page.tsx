import type { Metadata } from 'next';
import Header from '@/components/common/Header';
import DailySessionInteractive from './components/DailySessionInteractive';

export const metadata: Metadata = {
  title: 'Daily Session - InterviewNinja',
  description: 'Practice 10 customized technical and Computer Vision interview questions daily based on your profile resume and target job descriptions.',
};

export default function DailySessionPage() {
  return (
    <>
      <Header />
      <div className="min-h-screen bg-background pt-[60px]">
        <div className="page-wrapper">
          <div className="page-header">
            <h1 className="page-title">Daily Training Session</h1>
            <p className="page-subtitle">
              Generate 10 tailor-made questions covering core software engineering and advanced Computer Vision.
            </p>
          </div>
          <DailySessionInteractive />
        </div>
      </div>
    </>
  );
}
