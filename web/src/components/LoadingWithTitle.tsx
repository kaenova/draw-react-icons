import { PuffLoader } from "react-spinners";

export default function LoadingWithTitle({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center">
      <PuffLoader color="#E91E63" />
      <p className="font-bold">{children}</p>
    </div>
  );
}