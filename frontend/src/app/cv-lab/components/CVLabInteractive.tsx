'use client';

import { useState } from 'react';
import Icon from '@/components/ui/AppIcon';
import LabCopilot from '@/components/common/LabCopilot';
import OnDemandSection from '@/components/lab/OnDemandSection';
import QuizCarousel from '@/components/lab/QuizCarousel';

interface CVTopic {
  id: string; name: string; brief: string; category: string;
  prerequisites: string[]; subtopics: { id: string; name: string; brief: string }[];
}
interface SectionState { generated: boolean; generating: boolean; content: string }

const TOPICS: CVTopic[] = [
  {
    id: 'cnn', name: 'CNN Architectures', brief: 'Convolutional nets for visual feature learning.', category: 'Deep Learning',
    prerequisites: ['Linear Algebra', 'Backpropagation', 'Gradient Descent'],
    subtopics: [
      { id: 'resnet', name: 'ResNet & Skip Connections', brief: 'Residual learning to train very deep networks.' },
      { id: 'efficientnet', name: 'EfficientNet & Compound Scaling', brief: 'Principled scaling of depth, width, resolution.' },
      { id: 'mobilenet', name: 'MobileNet & Depthwise Convolutions', brief: 'Lightweight architecture for edge deployment.' },
    ],
  },
  {
    id: 'object-detection', name: 'Object Detection', brief: 'Localise and classify objects in images.', category: 'Detection',
    prerequisites: ['CNNs', 'Anchor Boxes', 'NMS'],
    subtopics: [
      { id: 'yolo', name: 'YOLO (v5/v8/v10)', brief: 'Single-stage real-time object detector.' },
      { id: 'faster-rcnn', name: 'Faster R-CNN & FPN', brief: 'Two-stage detector with region proposals.' },
      { id: 'detr', name: 'DETR (Detection Transformer)', brief: 'End-to-end detection with transformer attention.' },
    ],
  },
  {
    id: 'segmentation', name: 'Semantic & Instance Segmentation', brief: 'Pixel-level understanding of images.', category: 'Segmentation',
    prerequisites: ['Object Detection', 'Encoder-Decoder Architectures'],
    subtopics: [
      { id: 'unet', name: 'U-Net for Medical Imaging', brief: 'Skip connections for precise localisation.' },
      { id: 'mask-rcnn', name: 'Mask R-CNN', brief: 'Extends Faster R-CNN with a mask branch.' },
      { id: 'sam', name: 'Segment Anything (SAM)', brief: 'Foundation model for promptable segmentation.' },
    ],
  },
  {
    id: 'vit', name: 'Vision Transformers (ViT)', brief: 'Applying attention mechanisms to image patches.', category: 'Transformers',
    prerequisites: ['Self-Attention', 'Positional Encoding', 'CNNs'],
    subtopics: [
      { id: 'dino', name: 'DINO Self-Supervised ViT', brief: 'Knowledge distillation without labels.' },
      { id: 'swin', name: 'Swin Transformer', brief: 'Hierarchical ViT with shifted windows.' },
    ],
  },
  {
    id: 'classical', name: 'Classical Computer Vision', brief: 'Mathematical foundations before deep learning.', category: 'Classical',
    prerequisites: ['Linear Algebra', 'Calculus', 'Probability'],
    subtopics: [
      { id: 'feature-matching', name: 'SIFT / ORB Feature Matching', brief: 'Scale-invariant feature detection and matching.' },
      { id: 'stereo', name: 'Stereo Vision & Epipolar Geometry', brief: 'Depth from two cameras using geometry.' },
      { id: 'optical-flow', name: 'Optical Flow (Lucas-Kanade)', brief: 'Motion estimation between video frames.' },
    ],
  },
  {
    id: 'edge-deploy', name: 'Edge Deployment & Optimization', brief: 'Running CV models on constrained hardware.', category: 'MLOps',
    prerequisites: ['Model Architecture', 'PyTorch', 'Quantization basics'],
    subtopics: [
      { id: 'quantization', name: 'INT8/FP16 Quantization', brief: 'Reduce model size without significant accuracy loss.' },
      { id: 'pruning', name: 'Pruning & Knowledge Distillation', brief: 'Remove redundant weights or compress via a teacher.' },
      { id: 'tensorrt', name: 'TensorRT & ONNX Export', brief: 'NVIDIA-optimised inference runtime.' },
    ],
  },
];

function getContent(sectionId: string, topic: CVTopic): string {
  const name = topic.name;
  const prereqs = topic.prerequisites.join(', ');

  const templates: Record<string, string> = {
    prerequisites: `**Prerequisites for ${name}:**\n\n${topic.prerequisites.map((p, i) => `${i + 1}. **${p}** — Foundational understanding required before exploring this topic.`).join('\n')}\n\n**Why these matter:**\nWithout solid grounding in ${prereqs}, the mathematical derivations and intuition behind ${name} will be difficult to follow. Ensure you can derive backpropagation from scratch and understand matrix multiplication deeply.`,

    theory: `**Core Theory: ${name}**\n\n**Mathematical Foundation:**\nThe key operation is the discrete cross-correlation between an input feature map X and a learned filter K:\n\n(X ★ K)[i,j] = Σₘ Σₙ X[i+m, j+n] · K[m,n]\n\n**Key equations and concepts:**\n- Output spatial dimension: ⌊(W - F + 2P) / S⌋ + 1\n- Receptive field grows with depth: RF_l = RF_{l-1} + (F_l - 1) × S_prev\n- Parameter sharing: each filter has F×F×C_in parameters, shared across all spatial locations\n\n**Inductive biases baked in:**\n1. **Translation equivariance** — feature detected anywhere in image\n2. **Local connectivity** — nearby pixels are more related\n3. **Parameter sharing** — same feature detector used everywhere\n\n**What ViTs do differently:** No inductive bias — learns everything from data. Needs more data but generalises better at scale.`,

    visual: `**Visual Explanation & Architecture Flow**\n\nData flow through ${name}:\n\nInput Image [H×W×3]\n    ↓  Conv Layer 1 + BN + ReLU\n[H/2 × W/2 × 64]\n    ↓  Conv Layer 2 + BN + ReLU\n[H/4 × W/4 × 128]\n    ↓  ... (deeper stages)\n[H/32 × W/32 × 512]\n    ↓  Global Average Pooling\n[1 × 1 × 512]\n    ↓  Fully Connected\n[num_classes]\n\n**Key architectural choices:**\n- Batch Normalisation after every conv layer: stabilises training, allows higher LR\n- ReLU activation: sparse, computationally efficient, avoids vanishing gradient\n- Residual connections (ResNet): y = F(x) + x — gradient highway through identity mapping`,

    implementation: `**Practical Implementation in PyTorch**\n\n\`\`\`python\nimport torch\nimport torch.nn as nn\nimport torchvision.transforms as T\nfrom torchvision.models import resnet50, ResNet50_Weights\n\n# ── Standard Preprocessing Pipeline ──────────────────────────────────\ntransform_train = T.Compose([\n    T.RandomResizedCrop(224),          # Data augmentation\n    T.RandomHorizontalFlip(p=0.5),     # Flip augmentation\n    T.ColorJitter(0.2, 0.2, 0.2),     # Color augmentation\n    T.ToTensor(),\n    T.Normalize(                        # ImageNet statistics\n        mean=[0.485, 0.456, 0.406],\n        std=[0.229, 0.224, 0.225]\n    )\n])\n\n# ── Load Pretrained Model ─────────────────────────────────────────────\nmodel = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)\n\n# Replace head for fine-tuning\nnum_classes = 10\nmodel.fc = nn.Linear(model.fc.in_features, num_classes)\n\n# Freeze backbone, only train head\nfor param in model.parameters():\n    param.requires_grad = False\nfor param in model.fc.parameters():\n    param.requires_grad = True  # Only fine-tune the head\n\n# ── Training Loop ─────────────────────────────────────────────────────\noptimizer = torch.optim.AdamW(model.fc.parameters(), lr=1e-3, weight_decay=1e-4)\nscheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=50)\ncriterion = nn.CrossEntropyLoss(label_smoothing=0.1)  # Smoothing helps generalisation\n\nmodel.train()\nfor epoch in range(50):\n    for images, labels in dataloader:\n        images, labels = images.cuda(), labels.cuda()\n        \n        optimizer.zero_grad()\n        \n        with torch.cuda.amp.autocast():  # Mixed precision for speed\n            outputs = model(images)\n            loss = criterion(outputs, labels)\n        \n        scaler.scale(loss).backward()\n        scaler.step(optimizer)\n        scaler.update()\n    \n    scheduler.step()\n\`\`\``,

    hyperparameters: `**Hyperparameters & Design Choices**\n\n**Learning Rate (most critical):**\n- Start: 1e-3 for fine-tuning head, 1e-4 for full training\n- Schedule: CosineAnnealing or OneCycleLR — both work well\n- Rule of thumb: linear scaling with batch size (LR = base_lr × batch_size / 256)\n\n**Batch Size:**\n- 32-256 for most setups\n- Larger → more stable gradients, needs LR scaling\n- Too large → generalisation penalty (sharp minima)\n\n**Regularisation:**\n- Weight decay: 1e-4 (AdamW), 5e-4 (SGD)\n- Label smoothing: 0.1 — prevents overconfident predictions\n- Dropout: 0.2-0.5 before classifier head\n- Stochastic depth (DropPath): 0.1-0.2 for deep transformers\n\n**Data Augmentation priority (most impactful first):**\n1. Random crop + flip — always use\n2. Colour jitter — moderate effect\n3. MixUp / CutMix — +1-2% on ImageNet\n4. RandAugment — strong for small datasets`,

    pitfalls: `**Common Pitfalls & Debugging**\n\n**Training diverges (loss NaN or spikes):**\n- Check learning rate — likely too high\n- Check for NaN in inputs (normalise properly)\n- Gradient clipping: torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)\n- Check loss function — CrossEntropy expects raw logits, not softmax output\n\n**Model not converging:**\n- Verify data loading: print a batch, check labels are correct\n- Check normalisation — ImageNet stats don't apply to medical/satellite images\n- Overfit a single batch first — if it can't memorise 8 samples, architecture is wrong\n\n**Good validation metrics, poor production performance:**\n- Distribution shift — training and production data differ\n- Use adversarial validation to detect this\n- Add test-time augmentation (TTA) for robustness\n\n**Memory OOM:**\n- Reduce batch size or use gradient checkpointing\n- torch.cuda.empty_cache() between epochs\n- Use AMP (Automatic Mixed Precision) — halves memory`,

    applications: `**Real-World Applications of ${name}**\n\n**Autonomous Vehicles (Tesla, Waymo):**\n- Multi-camera perception stacks using CNN backbones\n- Real-time inference at 30+ FPS on automotive-grade hardware\n- Safety-critical → model uncertainty estimation is essential\n\n**Medical Imaging (Google Health, Paige.AI):**\n- Pathology slide analysis (gigapixel images)\n- Cancer detection at radiologist-level accuracy\n- Regulatory approval requires explainability (GRAD-CAM, SHAP)\n\n**Industrial Quality Control:**\n- Defect detection on production lines at 200+ FPS\n- Operates on edge devices (NVIDIA Jetson, Intel NCS)\n- Extremely high precision required (< 0.1% false positive)\n\n**Content Moderation (Meta, Google):**\n- Billions of images processed daily\n- Multi-label classification + severity scoring\n- Active learning pipeline to handle new violation types`,

    interview: `**Important Interview Questions — ${name}**\n\n**Conceptual:**\n1. What is the difference between semantic segmentation and instance segmentation?\n2. Why do we use batch normalisation and where exactly is it placed?\n3. Explain the vanishing gradient problem and how ResNet solves it.\n4. What are the inductive biases of CNNs vs Vision Transformers?\n\n**Design/Architecture:**\n5. How would you design a real-time object detection system for autonomous driving?\n6. How do you handle class imbalance in a medical image classification task?\n7. Walk me through how you'd fine-tune a pretrained model on a new domain.\n\n**Coding:**\n8. Implement a 2D convolution from scratch in Python/NumPy.\n9. Write the forward pass of a residual block.\n\n**Detailed Answers:**\nFor Q3: The skip connection y = F(x) + x means gradients flow directly back through the identity mapping. Even if F(x) has dying gradients, ∂L/∂x = ∂L/∂y · (∂F(x)/∂x + I) ≥ ∂L/∂y. This prevents vanishing.`,

    comparison: `**Comparison with Alternatives**\n\n| Approach | Strengths | Weaknesses | Best For |\n|---|---|---|---|\n| CNN | Translation equivariance, efficient, well-understood | Limited global context | Medium datasets, production |\n| ViT | Global attention, scales with data | Data hungry, computationally expensive | Large-scale datasets |\n| Hybrid (ConvNeXt) | Best of both worlds | More complex | General purpose SOTA |\n| Classical CV | Interpretable, no training data | Limited generalisation | Structured environments |\n\n**When to choose what:**\n- < 10k images → CNN + heavy augmentation (ViT will overfit)\n- > 1M images → ViT or hybrid (CNN bottlenecks at scale)\n- Latency < 10ms → Quantized MobileNet/EfficientNet-Lite\n- Interpretability required → Classical + GRAD-CAM for CNN`,

    paper: `**Research Context: ${name}**\n\n**Seminal Papers (chronological):**\n1. **LeNet-5 (LeCun, 1998)** — First practical CNN for digit recognition\n2. **AlexNet (Krizhevsky, 2012)** — Sparked deep learning revolution, ImageNet winner\n3. **VGGNet (Simonyan, 2014)** — Showed depth matters; 3×3 convolutions\n4. **ResNet (He, 2015)** — Skip connections; trained 152-layer networks\n5. **EfficientNet (Tan & Le, 2019)** — Compound scaling; NAS-found architecture\n6. **ViT (Dosovitskiy, 2020)** — "An image is worth 16×16 words"\n\n**Current state-of-the-art (2024):**\n- InternViT-6B, EVA, SigLIP — foundation models for vision\n- ConvNeXt V2 — CNN competitive with transformers at scale\n- DINOv2 — self-supervised ViT features transfer well\n\n**Key journals/venues:** CVPR, ICCV, ECCV, NeurIPS, ICLR, TPAMI`,

    references: `**References & Resources**\n\n📚 **Courses:**\n- CS231n (Stanford) — Convolutional Neural Networks for Visual Recognition (free online)\n- fast.ai Practical Deep Learning — top-down, code-first approach\n- d2l.ai — Dive into Deep Learning (interactive textbook)\n\n🔬 **Papers:**\n- Papers With Code (paperswithcode.com) — leaderboards + implementations\n- arXiv cs.CV — latest preprints\n- Semantic Scholar — citation tracking\n\n🛠️ **Code & Tools:**\n- PyTorch official tutorials (pytorch.org/tutorials)\n- Hugging Face timm library — 700+ pretrained CV models\n- torchvision models — standard backbone implementations\n- TIMM (Wightman) — state-of-the-art image models\n\n📹 **Videos:**\n- Yannic Kilcher (paper explanations)\n- Andrej Karpathy's lectures and talks`,
  };

  return templates[sectionId] ?? `**${name} — ${sectionId}**\n\nProfessional-grade content for this section covering ${name} in depth. This material is formatted for interview preparation and production engineering contexts.`;
}

const SECTION_DEFS = [
  { id: 'prerequisites', label: 'Prerequisites', icon: 'AcademicCapIcon', subtitle: 'What to know before diving in' },
  { id: 'theory', label: 'Core Theory', icon: 'CalculatorIcon', subtitle: 'Mathematical foundations + equations' },
  { id: 'visual', label: 'Visual Explanation & Architecture', icon: 'PhotoIcon', subtitle: 'Data flow diagrams + architecture' },
  { id: 'implementation', label: 'Practical Implementation', icon: 'CodeBracketIcon', subtitle: 'PyTorch code, end-to-end' },
  { id: 'hyperparameters', label: 'Hyperparameters & Design Choices', icon: 'AdjustmentsHorizontalIcon', subtitle: 'What to tune, typical values, tradeoffs' },
  { id: 'pitfalls', label: 'Common Pitfalls & Debugging', icon: 'BugAntIcon', subtitle: 'What goes wrong and how to fix it' },
  { id: 'applications', label: 'Real-World Applications', icon: 'BuildingOffice2Icon', subtitle: 'Industry use cases + company examples' },
  { id: 'interview', label: 'Important Interview Questions', icon: 'ChatBubbleLeftRightIcon', subtitle: 'Conceptual + coding + detailed answers' },
  { id: 'comparison', label: 'Comparison with Alternatives', icon: 'ScaleIcon', subtitle: 'Tradeoff table + when to use each' },
  { id: 'paper', label: 'Paper & Research Context', icon: 'DocumentMagnifyingGlassIcon', subtitle: 'Original paper + SOTA evolution' },
  { id: 'quiz', label: 'Quiz', icon: 'TrophyIcon', subtitle: '4 questions, score tracked, generate more' },
  { id: 'references', label: 'References & Resources', icon: 'BookOpenIcon', subtitle: 'CS231n, Papers With Code, PyTorch docs' },
];

const QUIZ_BANK = [
  { q: 'What inductive bias do CNNs have that ViTs lack?', options: ['Depth invariance', 'Translation equivariance + local connectivity', 'Global attention', 'Rotation invariance'], answer: 1, explanation: 'CNNs assume nearby pixels are correlated (local connectivity) and features should be detected regardless of position (translation equivariance). ViTs learn these from data with no such prior.' },
  { q: 'What problem do skip connections (ResNets) solve?', options: ['Overfitting', 'Vanishing gradients in deep networks', 'Slow inference', 'Large parameter count'], answer: 1, explanation: 'Skip connections create a gradient highway: ∂L/∂x includes an identity term (+I), ensuring gradients flow even through very deep networks.' },
  { q: 'What does IoU measure in object detection?', options: ['Model accuracy', 'Intersection over Union of predicted and ground truth boxes', 'Image quality score', 'Inference latency'], answer: 1, explanation: 'IoU = Area(Intersection) / Area(Union). Values > 0.5 are typically considered "correct" detections.' },
  { q: 'Why is batch normalisation placed before or after activation?', options: ['Always before', 'Always after', 'Before activation (pre-BN) for transformers, after for CNNs', 'The order doesn\'t matter'], answer: 2, explanation: 'Original ResNet uses BN → ReLU. Modern transformers use Pre-LN (norm before attention). Pre-BN generally trains more stably in very deep networks.' },
];

function initSections(): Record<string, SectionState> {
  return Object.fromEntries(SECTION_DEFS.map(s => [s.id, { generated: false, generating: false, content: '' }]));
}

export default function CVLabInteractive() {
  const [topics] = useState<CVTopic[]>(TOPICS);
  const [selectedTopicId, setSelectedTopicId] = useState('cnn');
  const [selectedSubtopicId, setSelectedSubtopicId] = useState<string | null>(null);
  const [expandedTopics, setExpandedTopics] = useState<Set<string>>(new Set(['cnn']));
  const [sections, setSections] = useState<Record<string, SectionState>>({});
  const [newTopicInput, setNewTopicInput] = useState('');
  const [addingTopic, setAddingTopic] = useState(false);
  const [customTopics, setCustomTopics] = useState<CVTopic[]>([]);
  const [quizBatch, setQuizBatch] = useState(0);

  const allTopics = [...topics, ...customTopics];
  const currentTopic = allTopics.find(t => t.id === selectedTopicId) ?? null;
  const currentSubtopic = currentTopic?.subtopics.find(s => s.id === selectedSubtopicId) ?? null;
  const contextLabel = currentSubtopic?.name ?? currentTopic?.name ?? 'Computer Vision';

  const flatItems = allTopics.flatMap(t => [
    { id: t.id, type: 'topic', topicId: t.id, label: t.name },
    ...t.subtopics.map(s => ({ id: s.id, type: 'subtopic', topicId: t.id, label: s.name })),
  ]);
  const activeId = selectedSubtopicId ?? selectedTopicId;
  const currentIdx = flatItems.findIndex(x => x.id === activeId);
  const prevItem = currentIdx > 0 ? flatItems[currentIdx - 1] : null;
  const nextItem = currentIdx >= 0 && currentIdx < flatItems.length - 1 ? flatItems[currentIdx + 1] : null;

  const navigateTo = (item: typeof flatItems[0]) => {
    setSelectedTopicId(item.topicId);
    setSelectedSubtopicId(item.type === 'subtopic' ? item.id : null);
    setSections(initSections());
    setQuizBatch(0);
    setExpandedTopics(prev => new Set([...prev, item.topicId]));
  };

  const selectTopic = (id: string) => {
    setSelectedTopicId(id);
    setSelectedSubtopicId(null);
    setSections(initSections());
    setQuizBatch(0);
    setExpandedTopics(prev => { const n = new Set(prev); n.has(id) ? n.delete(id) : n.add(id); return n; });
  };

  const selectSubtopic = (topicId: string, subId: string) => {
    setSelectedTopicId(topicId);
    setSelectedSubtopicId(subId);
    setSections(initSections());
    setQuizBatch(0);
    setExpandedTopics(prev => new Set([...prev, topicId]));
  };

  const generateSection = (sectionId: string) => {
    if (!currentTopic) return;
    setSections(prev => ({ ...prev, [sectionId]: { ...prev[sectionId], generating: true } }));
    setTimeout(() => {
      const content = getContent(sectionId, currentTopic);
      setSections(prev => ({ ...prev, [sectionId]: { generated: true, generating: false, content } }));
    }, 1500);
  };

  const handleAddTopic = () => {
    if (!newTopicInput.trim()) return;
    setAddingTopic(true);
    setTimeout(() => {
      const t: CVTopic = {
        id: `custom-${Date.now()}`, name: newTopicInput.trim(), brief: 'Custom CV topic.', category: 'Custom',
        prerequisites: ['Computer Vision Basics'],
        subtopics: [{ id: `sub-${Date.now()}`, name: 'Core Concepts', brief: 'Fundamental concepts.' }],
      };
      setCustomTopics(prev => [...prev, t]);
      setNewTopicInput('');
      setAddingTopic(false);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-background pt-[60px] flex flex-col">
      <div className="flex-1 flex overflow-hidden" style={{ height: 'calc(100vh - 60px)' }}>

        {/* ── LEFT: Topic Tree ────────────────────────────────────────────── */}
        <aside className="w-[260px] flex-shrink-0 border-r border-border bg-card flex flex-col">
          <div className="p-14 border-b border-border flex-shrink-0">
            <h2 className="font-heading text-sm font-semibold text-foreground flex items-center gap-9">
              <Icon name="EyeIcon" size={15} className="text-primary" />CV Lab
            </h2>
            <p className="text-xs text-muted-foreground mt-3">Select topic → Generate sections</p>
          </div>

          <div className="flex-1 overflow-y-auto py-6">
            {allTopics.map(topic => (
              <div key={topic.id}>
                <button onClick={() => selectTopic(topic.id)}
                  className={`w-full text-left flex items-center gap-8 px-14 py-9 text-xs font-semibold transition-smooth hover:bg-muted ${selectedTopicId === topic.id && !selectedSubtopicId ? 'bg-primary/10 text-primary border-r-2 border-primary' : 'text-foreground'}`}>
                  <Icon name="EyeIcon" size={12} />
                  <span className="flex-1 truncate">{topic.name}</span>
                  <span className="text-[10px] text-muted-foreground bg-muted px-5 py-2 rounded flex-shrink-0">{topic.category}</span>
                  <Icon name={expandedTopics.has(topic.id) ? 'ChevronDownIcon' : 'ChevronRightIcon'} size={11} className="text-muted-foreground flex-shrink-0" />
                </button>
                {expandedTopics.has(topic.id) && (
                  <div>
                    {topic.subtopics.map(sub => (
                      <button key={sub.id} onClick={() => selectSubtopic(topic.id, sub.id)}
                        className={`w-full text-left flex flex-col pl-26 pr-14 py-8 text-xs transition-smooth hover:bg-muted ${selectedSubtopicId === sub.id ? 'bg-secondary/10 text-secondary border-r-2 border-secondary' : 'text-muted-foreground'}`}>
                        <span className="font-medium truncate">↳ {sub.name}</span>
                        <span className="text-[10px] opacity-70 truncate mt-1">{sub.brief}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="p-12 border-t border-border flex-shrink-0">
            <div className="flex gap-6">
              <input value={newTopicInput} onChange={e => setNewTopicInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleAddTopic()}
                placeholder="Add custom topic..."
                className="flex-1 min-w-0 bg-input border border-border rounded-md px-9 py-6 text-xs focus-ring placeholder:text-muted-foreground" />
              <button onClick={handleAddTopic} disabled={addingTopic || !newTopicInput.trim()}
                className="p-6 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-smooth disabled:opacity-50 flex-shrink-0">
                {addingTopic ? <span className="w-12 h-12 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin block" /> : <Icon name="PlusIcon" size={14} />}
              </button>
            </div>
          </div>
        </aside>

        {/* ── CENTER ────────────────────────────────────────────────────────── */}
        <main className="flex-1 overflow-y-auto">
          {!currentTopic ? (
            <div className="flex flex-col items-center justify-center h-full text-center px-24">
              <Icon name="EyeIcon" size={48} variant="outline" className="text-muted-foreground/30 mb-18" />
              <h2 className="font-heading text-xl font-semibold text-foreground mb-9">Select a CV Topic</h2>
              <p className="text-sm text-muted-foreground max-w-sm">Choose a topic from the sidebar. Content generates on-demand per section.</p>
            </div>
          ) : (
            <div className="p-20 space-y-14">
              {/* Header */}
              <div className="bg-card border border-border rounded-lg p-20 shadow-sm">
                <div className="flex items-center gap-9 mb-9">
                  <span className="text-xs bg-primary/10 text-primary px-9 py-4 rounded-md">{currentTopic.category}</span>
                  {currentSubtopic && <span className="text-xs bg-secondary/10 text-secondary px-9 py-4 rounded-md">Subtopic</span>}
                </div>
                <h1 className="font-heading text-2xl font-bold text-foreground mb-6">
                  {currentSubtopic?.name ?? currentTopic.name}
                </h1>
                <p className="text-sm text-muted-foreground mb-12">{currentSubtopic?.brief ?? currentTopic.brief}</p>
                {currentTopic.prerequisites.length > 0 && (
                  <div className="flex flex-wrap gap-6">
                    <span className="text-xs text-muted-foreground">Prerequisites:</span>
                    {currentTopic.prerequisites.map(p => (
                      <span key={p} className="text-xs px-9 py-4 rounded-md bg-muted text-muted-foreground">{p}</span>
                    ))}
                  </div>
                )}
              </div>

              {/* On-demand sections */}
              {SECTION_DEFS.map((def, idx) => {
                const s = sections[def.id] ?? { generated: false, generating: false, content: '' };
                return (
                  <OnDemandSection key={def.id} sectionIndex={idx + 1} icon={def.icon} title={def.label} subtitle={def.subtitle}
                    content={s.content} isGenerated={s.generated} isGenerating={s.generating} onGenerate={() => generateSection(def.id)}>
                    {def.id === 'quiz' && s.generated ? (
                      <QuizCarousel questions={QUIZ_BANK.slice(quizBatch * 4, quizBatch * 4 + 4)} hasMore={true}
                        onGenerateMore={() => setQuizBatch(b => b + 1)} />
                    ) : undefined}
                  </OnDemandSection>
                );
              })}

              {/* Prev / Next */}
              <div className="flex items-center justify-between py-18 border-t border-border mt-24">
                <button disabled={!prevItem} onClick={() => prevItem && navigateTo(prevItem)}
                  className="flex items-center gap-9 px-16 py-10 rounded-md border border-border text-sm text-foreground hover:bg-muted transition-smooth disabled:opacity-30 disabled:pointer-events-none">
                  <Icon name="ArrowLeftIcon" size={14} />{prevItem?.label ?? 'No previous'}
                </button>
                <button disabled={!nextItem} onClick={() => nextItem && navigateTo(nextItem)}
                  className="flex items-center gap-9 px-16 py-10 rounded-md border border-border text-sm text-foreground hover:bg-muted transition-smooth disabled:opacity-30 disabled:pointer-events-none">
                  {nextItem?.label ?? 'No next'}<Icon name="ArrowRightIcon" size={14} />
                </button>
              </div>
            </div>
          )}
        </main>

        {/* ── RIGHT: Copilot ─────────────────────────────────────────────── */}
        <aside className="w-[280px] flex-shrink-0 border-l border-border flex flex-col">
          <LabCopilot context={contextLabel} labType="cv" />
        </aside>
      </div>
    </div>
  );
}
