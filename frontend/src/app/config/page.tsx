import type { Metadata } from 'next';
import Header from '@/components/common/Header';
import ConfigInteractive from './components/ConfigInteractive';

export const metadata: Metadata = {
  title: 'Settings - InterviewNinja',
  description: 'Configure your interview coach, LLM models, and API keys securely in your local environment.',
};

export default function ConfigPage() {
  return (
    <>
      <Header />
      <div className="min-h-screen bg-background pt-[60px]">
        <div className="max-w-[1000px] mx-auto px-24 py-36">
          <div className="mb-12">
            <h1 className="font-heading text-4xl font-semibold text-foreground mb-12">
              System Configuration
            </h1>
            <p className="text-muted-foreground font-body">
              Manage LLM APIs and set model architecture preferences for your daily interviews.
            </p>
          </div>
          <ConfigInteractive />
        </div>
      </div>
    </>
  );
}

