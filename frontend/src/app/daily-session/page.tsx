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
        <div className="max-w-[1400px] mx-auto px-24 py-36">
          <div className="mb-12">
            <h1 className="font-heading text-4xl font-semibold text-foreground mb-12">
              Daily Training Session
            </h1>
            <p className="text-muted-foreground font-body">
              Generate 10 tailor-made questions covering core software engineering and advanced Computer Vision.
            </p>
          </div>
          <DailySessionInteractive />
        </div>
      </div>
    </>
  );
}
