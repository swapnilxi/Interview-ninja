import type { Metadata } from 'next';
import Header from '@/components/common/Header';
import ProgressDashboardInteractive from '@/modules/progress-dashboard/ProgressDashboardModule';

export const metadata: Metadata = {
  title: 'Progress Dashboard - InterviewNinja',
  description: 'Track your interview preparation journey with comprehensive analytics, skill development trends, and personalized recommendations to assess your readiness.',
};

export default function ProgressDashboardPage() {
  return (
    <>
      <Header />
      <ProgressDashboardInteractive />
    </>
  );
}