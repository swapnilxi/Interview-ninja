export interface DSATopic {
  id: string;
  name: string;
  brief: string;
  category: string;
  difficulty: string;
  prerequisites: string[];
  subtopics: { id: string; name: string; brief: string }[];
  isCustom?: boolean;
}
