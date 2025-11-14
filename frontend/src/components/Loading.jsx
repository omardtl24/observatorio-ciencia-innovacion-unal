export default function Loading({ message = "Loading..." }) {
  return (
    <div className="flex items-center justify-center min-h-[50vh] flex-col gap-4">
      <div className="w-16 h-16 border-4 border-t-primary border-gray-200 rounded-full animate-spin"></div>
      <p className="text-gray-700">{message}</p>
    </div>
  );
}