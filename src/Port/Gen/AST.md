interface AST {
  declarations: Declaration[];
  generators: Generator[];
}

type Declaration = VariableDecl | FunctionDecl | ExternalDecl;

interface VariableDecl {
  type: "variable";
  name: string;
  varType?: "num" | "str" | "generator"; // 变量类型
  isConst?: boolean;
  initialValue?: Expression | GeneratorRef;
}

interface FunctionDecl {
  type: "function";
  name: string;
  parameters: string[];
  body: Block;
}

interface ExternalDecl {
  type: "external";
  name: string;
}

type Generator = {
  name: string;
  variants: GeneratorVariant[];
  annotations?: GeneratorAnnotation[];
};

type GeneratorVariant = {
  content: ContentElement[];
  children?: Generator[];
  weight?: number; // 权重值
};

type ContentElement = 
  | { type: "text"; value: string }
  | { type: "inlineChoice"; options: ContentElement[]; weights?: number[] }
  | { type: "generatorRef"; ref: string; postProcessors?: string[] }
  | { type: "variableRef"; ref: string; postProcessors?: string[] }
  | { type: "expression"; expr: Expression }
  | { type: "sideEffect"; assignment: Assignment }
  | { type: "repeat"; count: number | Expression; template: ContentElement[] }
  | { type: "match"; cases: MatchCase[] };

type GeneratorAnnotation = 
  | { type: "before"; block: Block }
  | { type: "after"; block: Block };

type Expression =
  | { type: "literal"; value: string | number }
  | { type: "variable"; name: string }
  | { type: "binaryOp"; op: string; left: Expression; right: Expression }
  | { type: "unaryOp"; op: string; operand: Expression }
  | { type: "functionCall"; name: string; args: Expression[] }
  | { type: "ternary"; condition: Expression; thenExpr: Expression; elseExpr: Expression }
  | { type: "array"; elements: Expression[] }
  | { type: "arrayAccess"; array: Expression; index: Expression };

type Assignment = {
  target: string;
  value: Expression | GeneratorRef;
};

type Block = Statement[];

type Statement = 
  | { type: "assignment"; assignment: Assignment }
  | { type: "expression"; expr: Expression }
  | { type: "sideEffect"; effect: Expression };

type MatchCase = {
  condition: Expression;
  result: ContentElement[];
};

type GeneratorRef = {
  generator: string;
  postProcessors?: string[];
};